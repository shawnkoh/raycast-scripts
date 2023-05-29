from sqlite_utils import Database
import dotenv
import json
from rich.pretty import pprint
from rich import inspect
import typer

app = typer.Typer()

# for each city, check if there are any items that can be bought and crafted for a profit
# ignore crafting bonuses for now
# 1. get a list of every craftable item
# 2. query the api to get their prices
# 3. for every craftable item, check the profitabiliy of crafting within the city


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


@app.command()
def init():
    db = Database("albion.db")
    dotenv.load_dotenv()
    ITEMS_PATH = "/Users/shawnkoh/repos/ao-data/ao-bin-dumps/items.json"
    items_file = open(ITEMS_PATH)
    items_json = json.load(items_file)

    craftable_items = list[dict]()
    parse_dict(craftable_items, items_json["items"])
    pprint(craftable_items)
    # pprint(items_json["items"])


# db["items"].insert()
