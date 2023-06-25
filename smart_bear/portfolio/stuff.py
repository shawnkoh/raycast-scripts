import ccxt.pro as ccxt
from rich.pretty import pprint
import pendulum
import dotenv
from datetime import datetime
import numpy as np
from functools import partial
import os
import uvloop
from expression import pipe
from expression.collections import seq, Seq, Map
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


from dydx3 import Client
from web3 import Web3
from dydx3.constants import NETWORK_ID_MAINNET, API_HOST_MAINNET
from sqlite_utils import Database
import pandas as pd

db = Database("binance.db")

dotenv.load_dotenv()

ETHEREUM_ADDRESS = os.getenv("DYDX_ADDRESS")

# Ganache node.
WEB_PROVIDER_URL = "https://mainnet.infura.io/v3/2452bd9413aa45b99cb27112e29a192d"

LIMIT = 1000
TIMEFRAME = "1h"


async def fetch_balance(exchange: ccxt.Exchange, type: str):
    balance = await exchange.fetch_balance(
        {
            "type": type,
        }
    )
    from expression.collections import map

    return pipe(
        balance["total"].items(),
        Map.of_seq,
        map.filter(lambda _, amount: amount > 0),
        dict,
    )


async def fetch_all_balance(exchange: ccxt.Exchange):
    await exchange.load_markets()
    balance = dict()

    async def concat_balance(type: str):
        latter = await fetch_balance(exchange, type)
        for symbol, amount in latter.items():
            if symbol in balance:
                balance[symbol] += amount
            else:
                balance[symbol] = amount

    await concat_balance("future")
    await concat_balance("delivery")
    await concat_balance("savings")
    await concat_balance("funding")
    await concat_balance("spot")
    return balance


async def get_data(exchange: ccxt.Exchange):
    earliest_timestamp = exchange.milliseconds()
    timeframe_duration_in_seconds = exchange.parse_timeframe(TIMEFRAME)
    timeframe_duration_in_ms = timeframe_duration_in_seconds * 1000
    timedelta = LIMIT * timeframe_duration_in_ms
    fetch_since = earliest_timestamp - timedelta

    # TODO: Bear in mind that this returns the current candle even when it has not closed
    fetch_ohlcv = partial(
        exchange.fetch_ohlcv, timeframe=TIMEFRAME, since=fetch_since, limit=LIMIT
    )

    async def get_df(symbol: str):
        response = await fetch_ohlcv(symbol)
        df = pd.DataFrame(
            response, columns=["Time", "Open", "High", "Low", "Close", "Volume"]
        )
        del df["Open"]
        del df["High"]
        del df["Low"]
        del df["Volume"]
        df["Time"] = [datetime.fromtimestamp(float(time) / 1000) for time in df["Time"]]
        df.set_index("Time", inplace=True)
        return df

    positions = await exchange.fetch_positions()

    positions = list(
        filter(
            lambda pos: pos["contracts"] > 0
            and pos["symbol"] != "USDC/USDT:USDT"
            and pos["symbol"] != "ETH/USDT:USDT",
            positions,
        )
    )

    symbols = set(map(lambda pos: pos["symbol"], positions))

    eth_df = await get_df("ETH/USDT")
    eth_returns = eth_df.pct_change()[1:]
    eth_returns_array = np.array(eth_returns["Close"])
    eth_reg = LinearRegression().fit(
        eth_returns_array.reshape(-1, 1),
        eth_returns_array.reshape(-1, 1),
    )

    for symbol in symbols:
        df = await get_df(symbol)
        returns = df.pct_change()[1:]

        # Check for linearity
        plt.figure()
        eth_returns["Close"].plot.kde(color="red", label="ETH")
        returns["Close"].plot.kde(color="green", label=symbol)
        plt.title("Linearity Check")
        plt.legend(loc="upper right", fontsize="large")
        plt.grid(True, which="both")
        plt.axvline(x=0, color="black", linestyle=":")
        plt.show()

        returns_array = np.array(returns["Close"])
        reg = LinearRegression().fit(
            eth_returns_array.reshape(-1, 1),
            returns_array.reshape(-1, 1),
        )
        # intercept coefficient aka Alpha
        alpha = float(eth_reg.intercept_)
        # slope coefficient aka Beta
        beta = float(reg.coef_)

        plt.figure()
        # plt.suptitle(
        #     f"Monthly Performance: {earliest_timestamp} - {fetch_since}",
        #     fontsize=14,
        # )
        plt.scatter(eth_returns_array, returns_array, color="blue", alpha=0.3)
        plt.plot(
            eth_returns_array.reshape(-1, 1),
            eth_reg.predict(eth_returns_array.reshape(-1, 1)),
            color="red",
            linewidth=2,
            label="ETH",
        )
        plt.plot(
            eth_returns_array.reshape(-1, 1),
            reg.predict(eth_returns_array.reshape(-1, 1)),
            color="blue",
            linewidth=2,
            label=f"{symbol}",
        )

        plt.title(
            f"""
{symbol}
{pendulum.from_timestamp(fetch_since / 1000).to_datetime_string()} - {pendulum.from_timestamp(earliest_timestamp / 1000).to_datetime_string()}
Timeframe: {TIMEFRAME}
Alpha:{alpha:.3f}
Beta: {beta:.3f}
""",
            {"fontsize": 16},
        )
        plt.ylabel("Percent Return of Token", {"fontsize": 16})
        plt.xlabel("Percent Return of ETH", {"fontsize": 16}, labelpad=10)
        # plt.xlim(-0.1, 0.1)
        # plt.ylim(-0.5, 0.5)
        # plt.yticks([-0.5, -0.25, 0, 0.25, 0.5])
        plt.grid(True, which="both")
        plt.axhline(y=0, color="black", linestyle=":")
        plt.axvline(x=0, color="black", linestyle=":")
        plt.legend(loc="upper right", fontsize="large")


async def get_dydx_balance():
    client = Client(
        network_id=NETWORK_ID_MAINNET,
        host=API_HOST_MAINNET,
        default_ethereum_address=ETHEREUM_ADDRESS,
        web3=Web3(Web3.HTTPProvider(WEB_PROVIDER_URL)),
        api_key_credentials={
            "walletAddress": ETHEREUM_ADDRESS,
            "secret": os.getenv("DYDX_API_SECRET"),
            "key": os.getenv("DYDX_API_KEY"),
            "passphrase": os.getenv("DYDX_API_PASSPHRASE"),
            "legacySigning": False,
            "walletType": "METAMASK",
        },
    )
    client.stark_private_key = {
        "walletAddress": ETHEREUM_ADDRESS,
        "publicKey": os.getenv("DYDX_STARK_PUBLIC_KEY"),
        "publicKeyYCoordinate": os.getenv("DYDX_STARK_PUBLIC_KEY_Y_COORDINATE"),
        "privateKey": os.getenv("DYDX_STARK_PRIVATE_KEY"),
        "legacySigning": False,
        "walletType": "METAMASK",
    }
    account_response = client.private.get_account().data["account"]
    return float(account_response["equity"])


async def balance_in_usdt(exchange: ccxt.Exchange):
    balance = await fetch_all_balance(exchange)

    tickers_query = []
    if exchange.id == "binance":
        tickers_query = ["BUSD/USDT"]

    usdt_value = 0
    for symbol, amount in balance.items():
        if amount == 0:
            continue
        if symbol == "USDT":
            usdt_value += amount
            continue

        symbol_usdt = symbol + "/USDT"
        symbol_busd = symbol + "/BUSD"

        if symbol_usdt in exchange.markets and exchange.markets[symbol_usdt]["active"]:
            tickers_query.append(symbol_usdt)
        elif (
            symbol_busd in exchange.markets and exchange.markets[symbol_busd]["active"]
        ):
            tickers_query.append(symbol_busd)
        else:
            raise Exception(symbol + " not in markets")

    tickers = await exchange.fetch_tickers(tickers_query)

    for symbol, amount in balance.items():
        if symbol == "USDT":
            continue
        symbol_usdt = symbol + "/USDT"
        symbol_busd = symbol + "/BUSD"
        if symbol_usdt in tickers:
            usdt_value += tickers[symbol_usdt]["last"] * amount
        elif symbol_busd in tickers:
            usdt_value += (
                tickers[symbol_busd]["last"] * amount * tickers["BUSD/USDT"]["last"]
            )
        else:
            raise Exception(symbol + " No usdt nor busd")

    return usdt_value


async def main(loop: uvloop.Loop):
    binance = ccxt.binance(
        {
            "apiKey": os.getenv("BINANCE_API_KEY"),
            "secret": os.getenv("BINANCE_SECRET"),
        }
    )
    await binance.load_markets()
    binance_usdt = round(await balance_in_usdt(binance), 2)
    pprint(f"Binance: {binance_usdt}")

    await get_data(binance)

    await binance.close()

    # bitmex = ccxt.bitmex(
    #     {
    #         "apiKey": os.getenv("BITMEX_API_KEY"),
    #         "secret": os.getenv("BITMEX_SECRET"),
    #     }
    # )
    # await bitmex.load_markets()
    # bitmex_usdt = round(await balance_in_usdt(bitmex), 2)
    # pprint(f"BITMEX: {bitmex_usdt}")
    # await bitmex.close()
    # dydx_usdc = round(await get_dydx_balance(), 2)
    # pprint(f"Dydx: {dydx_usdc}")
    loop.stop()
