import ccxt.pro as ccxt
from rich.pretty import pprint
import dotenv
import os
import uvloop
from expression import pipe
from expression.collections import seq, Seq, map, Map
from dydx3 import Client
from web3 import Web3
from dydx3.constants import NETWORK_ID_MAINNET, API_HOST_MAINNET


dotenv.load_dotenv()

ETHEREUM_ADDRESS = os.getenv("DYDX_ADDRESS")

# Ganache node.
WEB_PROVIDER_URL = "https://mainnet.infura.io/v3/2452bd9413aa45b99cb27112e29a192d"


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


async def fetch_balance(exchange: ccxt.Exchange, type: str):
    balance = await exchange.fetch_balance(
        {
            "type": type,
        }
    )
    return pipe(
        balance["total"].items(),
        Map.of_seq,
        map.filter(lambda _, amount: amount > 0),
        dict,
    )


async def balance_in_usdt(exchange: ccxt.Exchange):
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
    await binance.close()

    bitmex = ccxt.bitmex(
        {
            "apiKey": os.getenv("BITMEX_API_KEY"),
            "secret": os.getenv("BITMEX_SECRET"),
        }
    )
    await bitmex.load_markets()
    bitmex_usdt = round(await balance_in_usdt(bitmex), 2)
    pprint(f"BITMEX: {bitmex_usdt}")
    await bitmex.close()
    dydx_usdc = round(await get_dydx_balance(), 2)
    pprint(f"Dydx: {dydx_usdc}")
    loop.stop()
