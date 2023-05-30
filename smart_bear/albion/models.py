import pendulum
from cattrs.gen import make_dict_structure_fn, override
import attrs
import cattrs
from pendulum.datetime import DateTime, Timezone

GENESIS_DATE = DateTime(1, 1, 1, 0, 0, 0, tzinfo=Timezone("UTC"))

def is_genesis_date(datetime: DateTime):
    return datetime == GENESIS_DATE


@attrs.frozen
class ItemPrice:
    id: str
    city: str
    quality: int
    sell_price_min: float
    sell_price_min_date: DateTime
    sell_price_max: float
    sell_price_max_date: DateTime
    buy_price_min: float
    buy_price_min_date: DateTime
    buy_price_max: float
    buy_price_max_date: DateTime

    @property
    def can_market_buy():


@attrs.frozen
class CraftResource:
    id: str
    count: int
    max_return_amount: int | None = None


@attrs.frozen
class CraftingRequirement:
    time: float | None = None
    craft_resource: CraftResource | list[CraftResource] | None = None
    silver: float | None = None
    crafting_focus: float | None = None


@attrs.frozen
class CraftableItem:
    id: str
    crafting_requirements: CraftingRequirement | list[CraftingRequirement]


converter = cattrs.Converter()

converter.register_unstructure_hook(DateTime, lambda dt: dt.timestamp())

converter.register_structure_hook(DateTime, lambda ts, _: pendulum.parser.parse(ts))


converter.register_structure_hook(
    ItemPrice,
    make_dict_structure_fn(
        ItemPrice,
        converter,
        id=override(rename="item_id"),
    ),
)

converter.register_structure_hook(
    CraftResource,
    make_dict_structure_fn(
        CraftResource,
        converter,
        id=override(rename="@uniquename"),
        count=override(rename="@count"),
        max_return_amount=override(rename="@maxreturnamount"),
    ),
)

converter.register_structure_hook(
    CraftResource | list[CraftResource] | None,
    lambda craft_resource, _: [converter.structure(craft_resource, CraftResource)]
    if isinstance(craft_resource, dict)
    else converter.structure(craft_resource, list[CraftResource])
    if isinstance(craft_resource, list)
    else None,
)


converter.register_structure_hook(
    CraftingRequirement,
    make_dict_structure_fn(
        CraftingRequirement,
        converter,
        time=override(rename="@time"),
        silver=override(rename="@silver"),
        craft_resource=override(rename="craftresource"),
        crafting_focus=override(rename="@craftingfocus"),
    ),
)

converter.register_structure_hook(
    CraftingRequirement | list[CraftingRequirement],
    lambda crafting_requirement, _: [
        converter.structure(crafting_requirement, CraftingRequirement)
    ]
    if isinstance(crafting_requirement, dict)
    else converter.structure(crafting_requirement, list[CraftingRequirement]),
)

converter.register_structure_hook(
    CraftableItem,
    make_dict_structure_fn(
        CraftableItem,
        converter,
        id=override(rename="@uniquename"),
        crafting_requirements=override(rename="craftingrequirements"),
    ),
)
