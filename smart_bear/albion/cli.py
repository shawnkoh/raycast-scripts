from typing import Any, Callable
from sqlite_utils import Database
import dotenv
import json
import expression
from rich.pretty import pprint
from rich import inspect
import typer
import aiohttp
import aiorun
import uvloop
from .api import ApiClient


app = typer.Typer()

# for each city, check if there are any items that can be bought and crafted for a profit
# ignore crafting bonuses for now
# 1. get a list of every craftable item
# 2. query the api to get their prices
# 3. for every craftable item, check the profitabiliy of crafting within the city


def is_craftable_item(item: dict) -> bool:
    return "@uniquename" in item and "craftingrequirements" in item


def parse_dict(
    subject: dict,
    functor: Callable[
        [Any, dict],
        bool,
    ],
):
    if functor(subject):
        return

    for key, value in subject.items():
        if isinstance(value, dict):
            parse_dict(value, functor)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    parse_dict(item, functor)


def get_craftable_items(items: dict):
    result = list[dict]()

    @expression.curry(1)
    def functor(result: list[dict], item: dict) -> bool:
        if not is_craftable_item(item):
            return False

        result.append(item)
        return True

    parse_dict(items, functor(result))
    return result


def get_unique_names(items: dict):
    result = set[str]()

    @expression.curry(1)
    def functor(result: set[str], item: dict) -> bool:
        if "@uniquename" not in item:
            return False

        result.add(item["@uniquename"])
        return True

    parse_dict(items, functor(result))
    return result


async def main(loop: uvloop.Loop):
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=None))
    api_client = ApiClient(session)
    db = Database("albion.db")
    dotenv.load_dotenv()
    ITEMS_PATH = "/Users/shawnkoh/repos/ao-data/ao-bin-dumps/items.json"
    items_file = open(ITEMS_PATH)
    items_json = json.load(items_file)

    unique_names = get_unique_names(items_json)
    craftable_items = get_craftable_items(items_json)

    def craft_resource_crafting_cost(craft_resource: dict):
        total_silver = 0
        count = float(craft_resource["@count"])

        # TODO: "@maxreturnamount"
        # Note that this affects focus calculations
        max_return_amount = (
            float(craft_resource["@maxreturnamount"])
            if "@maxreturnamount" in craft_resource
            else None
        )

        if "@silver" in craft_resource:
            total_silver += float(craft_resource["@silver"]) * count

        return total_silver

    # This assumes that you have the ingredients ready.
    # It does not recurse.
    def get_crafting_cost(item_id: str):
        total_silver = 0
        craftable_item = db["craftable_items"].get(price["item_id"])
        crafting_requirements = json.loads(craftable_item["craftingrequirements"])

        # NB: An item can have multiple crafting requirements
        for requirement in crafting_requirements:
            if "@silver" in requirement:
                total_silver += float(requirement["@silver"])

            craft_resource = requirement["craftresource"]
            if isinstance(craft_resource, dict):
                total_silver += craft_resource_crafting_cost(craft_resource)
            elif isinstance(craft_resource, list):
                for resource in craft_resource:
                    total_silver += craft_resource_crafting_cost(resource)
            else:
                raise Exception()

        return total_silver

    db["craftable_items"].insert_all(
        craftable_items,
        pk="@uniquename",
        replace=True,
        alter=True,
    )

    prices = db.query(
        """
    SELECT *
    FROM prices
    WHERE sell_price_min > 0
    """
    )
    for price in prices:
        pprint(price)
        crafting_cost = get_crafting_cost(price["item_id"])
        print(
            f"""
item_id = {price["item_id"]}
crafting_cost = {crafting_cost}
"""
        )
        break

    # for craftable_item in craftable_items:
    #     crafting_requirements = craftable_item["craftingrequirements"]
    #     silver_cost = float(crafting_requirements["@silver"])
    #     crafting_focus = (
    #         float(crafting_requirements["@craftingfocus"])
    #         if "@craftingfocus" in crafting_requirements
    #         else None
    #     )
    #     if "craftresource" in crafting_requirements:
    #         for craft_resource in crafting_requirements["craftresource"]:
    #             "@uniquename"

    #             if "@craftingfocus" in craft_resource:
    #             "@count"
    # some cannot have return eg artifacts
    # "@maxreturnamount"

    # sell price is literally the price the market is selling
    # same for buying

    # pprint(unique_names)

    # prices = await api_client.get_prices(unique_names)

    # db["prices"].insert_all(
    #     prices,
    #     pk=("item_id", "city", "quality"),
    #     replace=True,
    #     alter=True,
    # )

    # for every craftable item
    # figure out how much is the cost of crafting
    # ignore the item if its not sellable
    # ignore the item if the ingredients are not purchasable
    # maybe - for a start, restrict by city only to martlock

    # to compute craftable items
    # first, i need to get the sell price of that item

    await session.close()
    loop.stop()


@app.command()
def init():
    loop = uvloop.new_event_loop()
    aiorun.run(main(loop), loop=loop)

    # pprint(craftable_items)
    # pprint(items_json["items"])


# db["items"].insert()
