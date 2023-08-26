import itertools
import logging
import re
from asset_ripper_parser.exported_file_parser import parse_exported_file
from asset_ripper_parser.index_files import FileIndexer
from asset_ripper_parser.models.item import Item
from asset_ripper_parser.parse_sprite_sheet import parse_sprite_asset


def parse_item(
    indexer: FileIndexer, item_component: dict, item: Item, sprite_guid=None
) -> Item:
    """Given a dict of item data, applies its properties to the provided Item object.
    The data that's parsed here is namely the name, id, rarity, hearts, and sell price.

    Args:
        indexer (FileIndexer): used to look up the sprite for the item.
        item_component (dict): MonoBehaviour of the item asset
        item (Item): original item that needs data
        parse_sprite (str, optional):   If provided, will look up the image for this item.
                                        Defaults to None.

    Returns:
        Item: original item with generic properties applied
    """
    item.item_id = item_component["id"]
    item.stack_size = item_component["stackSize"]
    item.hearts = item_component["hearts"]
    item.rarity = item_component["rarity"]
    item.is_dlc = item_component["isDLCItem"] == 1

    if "description" in item_component and item_component["description"] is not None:
        item.description = item_component["description"]

    if sprite_guid is not None:
        sprite_path = indexer.find_sprite_path_from_guid(sprite_guid)
        if sprite_path is not None:
            item.sprite = parse_sprite_asset(indexer, sprite_path)

    if item_component["sellPrice"] > 0:
        item.sells_for = item_component["sellPrice"]
        item.sell_type = "Coins"
    elif item_component["orbsSellPrice"] > 0:
        item.sells_for = item_component["orbsSellPrice"]
        item.sell_type = "Orbs"
    elif item_component["ticketSellPrice"] > 0:
        item.sells_for = item_component["ticketSellPrice"]
        item.sell_type = "Tickets"

    return item


def produce_description_template(items: list[Item]) -> str:
    output = ""
    items.sort(key=lambda x: x.name)
    default = (
        "    |#default=Edit in https://sun-haven.fandom.com/wiki/Template:Description "
        + "<!--if the item doesn't have a listing here, it will show this-->}}\n"
    )

    output += (
        "<includeonly><!--1.2.0-->{{#switch:{{lc:{{#sub:{{{1|{{PAGENAME}}}}}|0|1}} }}\n"
    )
    output += "<!-- example: |name(lower case letters)=Description -->\n"

    for key, group in itertools.groupby(items, lambda x: x.name.lower()[0]):
        output += f"|{key}=" + "{{#switch:{{lc:{{{1|{{PAGENAME}}}}}}}\n"
        for shared_description_key, shared_descriptions in itertools.groupby(
            group, lambda x: x.description
        ):
            item_names = set(x.name.lower() for x in shared_descriptions)
            clean_description = (
                re.sub(
                    r"<color=#[A-Z0-9]+>\([\w\s]+\)<\/color>",
                    "",
                    shared_description_key,
                )
                .replace("</b>", "'''")
                .replace("<b>", "'''")
            )

            clean_description = re.sub(r"\s{2,}", " ", clean_description)

            if clean_description != "":
                output += f"    |{'|'.join(item_names)}={clean_description}\n"
        output += default

    output += "|#default=Edit in https://sun-haven.fandom.com/wiki/Template:Description"
    output += "}}</includeonly><noinclude>{{documentation}}</noinclude>"
    return output


def parse_items(
    indexer: FileIndexer,
    item_paths: list[str],
    report_progress=None,
    parse_sprite=False,
) -> list[Item]:
    """Given a list of file paths, returns a list of items.

    Args:
        indexer (FileIndexer):  used to look up the icon/sprite for this item.
                                Currently not doing that.
        item_paths (list[str]): all asset file paths with item information.
        report_progress (function, optional): Called when an item has been parsed. Defaults to None.
        parse_sprite (bool): If true, will look up sprite and apply it to the returned object. Defaults to False.

    Returns:
        list[Item]: List of parsed items.
    """
    items = []
    for path in item_paths:
        try:
            item_component = parse_exported_file(path)[0]["MonoBehaviour"]
            item = Item(item_component["name"])

            icon = None
            if parse_sprite:
                icon = item_component["icon"]["guid"]

            item = parse_item(indexer, item_component, item, sprite_guid=icon)

            if report_progress is not None:
                report_progress()
            items.append(item)
        except:
            logging.error("Could not parse %s", path, exc_info=True)
    return items
