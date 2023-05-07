import ccxt.pro as ccxt
from rich.pretty import pprint
import dotenv
import os
import uvloop
from expression import pipe
from expression.collections import seq, Seq, map, Map

dotenv.load_dotenv()


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
    binance_usdt = await balance_in_usdt(binance)
    pprint(f"Binance: {binance_usdt}")
    await binance.close()

    bitmex = ccxt.bitmex(
        {
            "apiKey": os.getenv("BITMEX_API_KEY"),
            "secret": os.getenv("BITMEX_SECRET"),
        }
    )
    await bitmex.load_markets()
    bitmex_usdt = await balance_in_usdt(bitmex)
    pprint(f"BITMEX: {bitmex_usdt}")
    await bitmex.close()
    loop.stop()
