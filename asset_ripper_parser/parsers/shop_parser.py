"""Functions for parsing shop asset files."""
import logging
import os
from asset_ripper_parser.parse_exported_file import parse_exported_file
from asset_ripper_parser.utils import camel_case_split
from asset_ripper_parser.index_files import FileIndexer
from asset_ripper_parser.models.item import Item
from asset_ripper_parser.models.shop import RandomSelection, Shop, SoldItem


def parse_sold_item(indexer: FileIndexer, selling_item: dict) -> Item:
    """Given a dict of data from merchant table item list, creates a SoldItem.
    The data that's parsed here is namely the name, id, rarity, hearts, and sell price.

    Args:
        indexer (FileIndexer): used to look up the sprite for the item.
        selling_item (dict): dict containing amount, price, item, etc. from a merchant table.

    Returns:
        SoldItem: about this item in the shop.
    """
    item_name = indexer.find_name_from_guid(selling_item["item"]["guid"])
    item = SoldItem(item_name)

    if selling_item["itemToUseAsCurrency"]["fileID"] != 0:
        item.price = selling_item["price"]
        item.price_type = (
            indexer.find_name_from_guid(selling_item["itemToUseAsCurrency"]["guid"])
            + "s"
        )
    elif selling_item["price"] > 0:
        item.price = selling_item["price"]
        item.price_type = "Coins"
    elif selling_item["orbs"] > 0:
        item.price = selling_item["orbs"]
        item.price_type = "Orbs"
    elif selling_item["tickets"] > 0:
        item.price = selling_item["tickets"]
        item.price_type = "Tickets"

    if "qty" in selling_item and selling_item["isLimited"] == 1:
        item.quantity = selling_item["qty"]

    if "chance" in selling_item:
        item.stock_chance = selling_item["chance"]

    if "resetDay" in selling_item:
        item.restock_days = selling_item["resetDay"]

    item.limited = "isLimited" in selling_item and selling_item["isLimited"] == 1

    return item


def parse_merchant_table(
    indexer: FileIndexer, merchant_table: dict, shop: Shop
) -> Shop:
    """Parse a merchant table referenced from a shop asset.

    Args:
        indexer (FileIndexer): used to look up items sold.
        merchant_table (dict):  should contain 'startingItems' and
                                potentially empty 'randomShopItems'.
        shop (Shop): where the items are sold.

    Returns:
        Shop: original shop parameter with parsed data applied.
    """
    always_items = []
    for selling_item in merchant_table["startingItems"]:
        item = parse_sold_item(indexer, selling_item)
        always_items.append(item)

    shop.always_stocked_items = always_items

    random_selections = []
    for selection in merchant_table["randomShopItems"]:
        random_selection = RandomSelection()
        random_selection.selection_name = selection["tableName"]
        random_selection.amount_selected = selection["randomShopItemAmount"]

        for selling_item in selection["shopItems"]:
            item = parse_sold_item(indexer, selling_item)
            random_selection.items.append(item)
        random_selections.append(random_selection)

    shop.random_selections = random_selections

    # This removes items if they are variants of the same type.
    shop.combine_colored_items()

    return shop


def parse_merchants(
    indexer: FileIndexer, paths: list[str], report_progress=None
) -> list[Shop]:
    """Given a list of shop file paths, returns a list of shops.

    Args:
        indexer (FileIndexer):  used to look up the icon/sprite for this item.
                                Currently not doing that.
        item_paths (list[str]): all asset file paths with item information.
        report_progress (_type_, optional): Called when an item has been parsed. Defaults to None.

    Returns:
        list[Item]: List of parsed items.
    """
    shops = []
    for path in paths:
        try:
            parsed_merchant = parse_exported_file(path)
            relevant_component = [
                x
                for x in parsed_merchant
                if "MonoBehaviour" in x and "startingItems" in x["MonoBehaviour"]
            ]

            merchant_component = relevant_component[0]["MonoBehaviour"]
            shop = Shop()
            shop.shop_name = (
                os.path.basename(path)
                .replace(".prefab", "")
                .replace(".asset", "")
                .replace("_", "")
                .replace("MerchantTable", "")
            )

            shop.shop_name = camel_case_split(shop.shop_name)

            shop = parse_merchant_table(indexer, merchant_component, shop)

            if report_progress is not None:
                report_progress()
            shops.append(shop)
        except:
            logging.error("Could not parse %s", path, exc_info=True)
    return shops


def parse_shops(
    indexer: FileIndexer, shop_paths: list[str], report_progress=None
) -> list[Shop]:
    """Given a list of shop file paths, returns a list of shops.

    Args:
        indexer (FileIndexer):  used to look up the icon/sprite for this item.
                                Currently not doing that.
        item_paths (list[str]): all asset file paths with item information.
        report_progress (_type_, optional): Called when an item has been parsed. Defaults to None.

    Returns:
        list[Item]: List of parsed items.
    """
    shops = []
    for path in shop_paths:
        try:
            parsed_shop = parse_exported_file(path)
            relevant_component = [
                x
                for x in parsed_shop
                if "MonoBehaviour" in x and "merchantTable" in x["MonoBehaviour"]
            ]

            shop_component = relevant_component[0]["MonoBehaviour"]
            shop = Shop()
            shop.shop_name = shop_component["shopName"]
            shop.seller_name = os.path.basename(path).replace(".prefab", "")

            merchant_table_path = indexer.find_filepath_from_guid(
                shop_component["merchantTable"]["guid"]
            )
            if merchant_table_path is not None:
                merchant_table = parse_exported_file(merchant_table_path)[0][
                    "MonoBehaviour"
                ]
                shop = parse_merchant_table(indexer, merchant_table, shop)

            if report_progress is not None:
                report_progress()
            shops.append(shop)
        except:
            logging.error("Could not parse %s", path, exc_info=True)
    return shops
