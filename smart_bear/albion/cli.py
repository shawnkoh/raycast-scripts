from typing import Any, Callable, Optional
from sqlite_utils import Database
from sqlite_utils.db import NotFoundError
import json
import attrs
import expression
from rich.pretty import pprint
from rich import inspect
import typer
import aiohttp
import aiorun
import uvloop
from .api import ApiClient
from .models import (
    ItemPrice,
    CraftableItem,
    CraftResource,
    CraftingRequirement,
    converter,
)

ITEMS_PATH = "/Users/shawnkoh/repos/ao-data/ao-bin-dumps/items.json"


app = typer.Typer()


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


@attrs.frozen
class IngredientCost:
    item_price: ItemPrice
    count: int


@attrs.define
class ProductCost:
    id: str
    quality: int
    silver: float
    time: float
    crafting_focus: float
    ingredient_costs: list[IngredientCost]


@attrs.define
class Albion:
    api_client: ApiClient
    db: Database

    @property
    def items(self):
        items_file = open(ITEMS_PATH)
        return json.load(items_file)

    @property
    def unique_names(self):
        return get_unique_names(self.items)

    async def update_prices(self):
        unique_names = get_unique_names(self.items)
        prices = await self.api_client.get_prices(unique_names)

        self.db["prices"].insert_all(
            prices,
            pk=(
                "item_id",
                "quality",
                "city",
            ),
            replace=True,
            alter=True,
        )

    def update_craftable_items(self):
        craftable_items = get_craftable_items(self.items)

        self.db["craftable_items"].insert_all(
            craftable_items,
            pk="@uniquename",
            replace=True,
            alter=True,
        )

    def get_craftable_item(self, id: str):
        try:
            row = self.db["craftable_items"].get(id)
            row["craftingrequirements"] = json.loads(row["craftingrequirements"])
            return converter.structure(row, CraftableItem)
        except NotFoundError:
            return None

    def get_item_prices(self):
        prices = self.db.query(
            """
        SELECT *
        FROM prices
        WHERE sell_price_min > 0
        """
        )
        for price in prices:
            yield converter.structure(price, ItemPrice)

    def get_item_price(self, id: str, quality: int, city: str):
        row = self.db["prices"].get((id, quality, city))
        return converter.structure(row, ItemPrice)

    def get_ingredient_cost(
        self,
        craft_resource: CraftResource,
        quality: int,
        city: str,
    ):
        item_price = self.get_item_price(craft_resource.id, quality, city)
        return IngredientCost(item_price, craft_resource.count)

    def get_product_cost(
        self,
        id: str,
        quality: int,
        city: str,
        crafting_requirement: CraftingRequirement,
    ) -> ProductCost:
        product_cost = ProductCost(
            id,
            quality,
            crafting_requirement.silver
            if crafting_requirement.silver is not None
            else 0,
            crafting_requirement.time if crafting_requirement.time is not None else 0,
            crafting_requirement.crafting_focus
            if crafting_requirement.crafting_focus is not None
            else 0,
            [],
        )
        return product_cost

    # NB: This assumes the ingredients are bought in the same city
    # it should return an array of paths because there are multiple ways to craft
    def get_product_costs(self, item_price: ItemPrice):
        product_costs = list[ProductCost]()

        craftable_item = self.get_craftable_item(item_price.id)

        if craftable_item is None:
            # TODO: Handle this
            raise Exception()

        for crafting_requirement in craftable_item.crafting_requirements:
            crafting_requirement: CraftingRequirement

            product_cost = ProductCost(item_price.id, 0, 0, 0, [])

            if crafting_requirement.silver is not None:
                total_silver += crafting_requirement.silver

            for craft_resource in crafting_requirement.craft_resource:
                craft_resource: CraftResource
                craft_resource.id

        return product_costs

        # for each city, check if there are any items that can be bought and crafted for a profit
        # ignore crafting bonuses for now
        # 1. get a list of every craftable item
        # 2. query the api to get their prices
        # 3. for every craftable item, check the profitabiliy of crafting within the city


async def main(loop: uvloop.Loop):
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=None))
    api_client = ApiClient(session)
    db = Database("albion.db")
    albion = Albion(api_client, db)
    albion.update_craftable_items()
    # await albion.update_prices()

    prices = db.query(
        """
    SELECT *
    FROM prices
    WHERE sell_price_min > 0
    """
    )

    # for each city, check if there are any items that can be bought and crafted for a profit
    # ignore crafting bonuses for now
    # 1. get a list of every craftable item
    # 2. query the api to get their prices
    # 3. for every craftable item, check the profitabiliy of crafting within the city
    for price in prices:
        item_price = converter.structure(price, ItemPrice)
        pprint(item_price)
        craftable_item = albion.get_craftable_item(item_price.id)
        # TODO: Handle this
        if craftable_item is None:
            continue
        pprint(craftable_item)
        for crafting_requirement in craftable_item.crafting_requirements:
            crafting_requirement: CraftingRequirement
            for resource in crafting_requirement.craft_resource:
                resource: CraftResource

    # sell price is literally the price the market is selling
    # same for buying

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
