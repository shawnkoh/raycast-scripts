from sqlite_utils import Database
import dotenv
import json
from rich.pretty import pprint
from rich import inspect
import typer
import aiohttp
import aiorun
import uvloop

app = typer.Typer()

# for each city, check if there are any items that can be bought and crafted for a profit
# ignore crafting bonuses for now
# 1. get a list of every craftable item
# 2. query the api to get their prices
# 3. for every craftable item, check the profitabiliy of crafting within the city

API_URL = "https://east.albion-online-data.com/api/v2/stats"
MAX_URL_LENGTH = 4096


class ApiClient:
    client: aiohttp.ClientSession

    def __init__(self, client: aiohttp.ClientSession) -> None:
        self.client = client

    async def get_prices(self, name_list: list[str], format: str = "json"):
        assert len(name_list) > 0

        result = list()

        url = f"{API_URL}/Prices/"
        format_suffix = f".{format}"
        max_url_length = MAX_URL_LENGTH - len(url) - len(format_suffix)

        url_chunks = list[str]()
        url_chunk = ""

        for index, name in enumerate(name_list):
            new_url_chunk = f"{url_chunk}{'' if url_chunk == '' else ','}{name}"

            if len(new_url_chunk) > max_url_length:
                url_chunks.append(f"{url}{url_chunk}{format_suffix}")
                url_chunk = name
            else:
                url_chunk = new_url_chunk

            if len(name_list) == index + 1:
                url_chunks.append(f"{url}{url_chunk}{format_suffix}")

        for url_chunk in url_chunks:
            pprint(url_chunk)
            async with self.client.get(url_chunk) as response:
                result_chunk = await response.json()
                pprint(result_chunk)
                result.append(result_chunk)

        return result


def is_craftable_item(item: dict) -> bool:
    return "@uniquename" in item and "craftingrequirements" in item


def do_dict(subject: dict):
    if not is_craftable_item(subject):
        pass


def parse_dict(craftable_items: list[dict], subject: dict):
    if is_craftable_item(subject):
        craftable_items.append(subject)
        return

    for key, value in subject.items():
        if isinstance(value, dict):
            parse_dict(craftable_items, value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    parse_dict(craftable_items, item)


async def main(loop: uvloop.Loop):
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=None))
    api_client = ApiClient(session)
    db = Database("albion.db")
    dotenv.load_dotenv()
    ITEMS_PATH = "/Users/shawnkoh/repos/ao-data/ao-bin-dumps/items.json"
    items_file = open(ITEMS_PATH)
    items_json = json.load(items_file)

    craftable_items = list[dict]()
    parse_dict(craftable_items, items_json["items"])

    craftable_items_uniquename = list()
    for item in craftable_items:
        craftable_items_uniquename.append(item["@uniquename"])

    prices = await api_client.get_prices(craftable_items_uniquename)
    # pprint(prices)

    await session.close()
    loop.stop()


@app.command()
def init():
    loop = uvloop.new_event_loop()
    aiorun.run(main(loop), loop=loop)

    # pprint(craftable_items)
    # pprint(items_json["items"])


# db["items"].insert()
