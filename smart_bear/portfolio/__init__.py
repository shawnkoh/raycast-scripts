import ccxt.pro as ccxt
from rich.pretty import pprint
import dotenv
import os
import uvloop
from expression import pipe
from expression.collections import seq, Seq, map, Map

dotenv.load_dotenv()


async def main(loop: uvloop.Loop):
    exchange = ccxt.binance(
        {
            "apiKey": os.getenv("BINANCE_API_KEY"),
            "secret": os.getenv("BINANCE_SECRET"),
        }
    )
    await exchange.load_markets()
    balance = await exchange.fetch_balance()
    balance = pipe(
        balance["total"].items(),
        Map.of_seq,
        map.filter(lambda _, amount: amount > 0),
        dict,
    )

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

    pprint(usdt_value)
    await exchange.close()
    loop.stop()
