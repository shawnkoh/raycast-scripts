import ccxt.pro as ccxt
import asyncio
from rich.pretty import pprint


async def main():
    exchange = ccxt.binance()
    pprint(await exchange.fetch_balance())


asyncio.run(main())
