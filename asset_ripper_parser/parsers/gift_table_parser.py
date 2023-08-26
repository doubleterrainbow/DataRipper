"""All methods used to parse GiftTables."""
import logging
import pprint
import re
from asset_ripper_parser.parse_exported_file import parse_exported_file
from asset_ripper_parser.index_files import FileIndexer
from asset_ripper_parser.models.gift_table import (
    GiftLevel,
    GiftTable,
    UniqueGiftResponse,
)


def clean_text(text):
    """Removes junk from text, like italic formatting characters and colors.

    Args:
        text (str): dialogue from game.

    Returns:
        str: dialogue more usable on the wiki.
    """
    result = text.replace("<i>", "''").replace("</i>", "''").replace("</color>", "")
    return re.sub(r"<color=#[0-9]+>", "", result)


def parse_gift_section(indexer: FileIndexer, component, gift_level, gift_table):
    """
    Parses a GiftLevel worth of data from a gift table asset.

    Args:
        indexer (FileIndexer): used for file lookups
        component (dict): relevant section of the gift table
        gift_level (GiftLevel): current gift level we are parsing
        gift_table (GiftTable): GiftTable to add data to.

    Returns:
        GiftTable: original GiftTable with parsed data applied.
    """
    if gift_level not in [GiftLevel.UNIQUE, GiftLevel.NEUTRAL]:
        parsed_items = []
        items = component[gift_level.value]

        for item in items:
            guid = item["guid"]
            item_name = indexer.find_name_from_guid(guid)

            parsed_items.append(item_name)

        if gift_level == GiftLevel.LOVE:
            gift_table.loved.items = parsed_items
            gift_table.loved.responses = [
                clean_text(x) for x in component[f"{gift_level.value}Responses"]
            ]
        elif gift_level == GiftLevel.LIKE:
            gift_table.liked.items = parsed_items
            gift_table.liked.responses = [
                clean_text(x) for x in component[f"{gift_level.value}Responses"]
            ]
        elif gift_level == GiftLevel.DISLIKE:
            gift_table.disliked.items = parsed_items
            gift_table.disliked.responses = [
                clean_text(x) for x in component[f"{gift_level.value}Responses"]
            ]
    else:
        if gift_level == GiftLevel.UNIQUE:
            parsed_items = []
            items = component["uniqueGifts"]
            for item in items:
                guid = item["item"]["guid"]
                item_name = indexer.find_name_from_guid(guid)
                response = item["response"]

                parsed_items.append(UniqueGiftResponse(item_name, clean_text(response)))

            gift_table.unique_items = parsed_items
        elif gift_level == GiftLevel.NEUTRAL:
            items = component[gift_level.value]
            neutral_items = []
            for item in items:
                item_filepath = indexer.find_filepath_from_guid(item["guid"])
                if item_filepath is not None:
                    item_data = parse_exported_file(item_filepath)[0]["MonoBehaviour"]
                    if item_data["hearts"] != 1:
                        neutral_items.append(item_data["name"])
            gift_table.neutral.items = neutral_items
            gift_table.neutral.responses = [
                clean_text(x) for x in component[f"{gift_level.value}Responses"]
            ]
    return gift_table


def parse_gift_tables(indexer: FileIndexer, filepaths: list[str], report_progress=None):
    """Given a list of file paths, returns a list of GiftTable objects.

    Each file is opened and read for relevant data.

    Args:
        indexer (FileIndexer): used for file lookups
        filepaths (list[str]): file paths like <RNPC_NAME>GiftTable.asset
        report_progress (function, optional): Runs every time a gift table is parsed.
                                            Defaults to None.

    Returns:
        list[GiftTable]: parsed GiftTable objects containing data relevant to a RNPC
    """
    tables = []
    for path in filepaths:
        gift_table = GiftTable()
        gift_table.npc_name = path.split("gift tables\\")[1].replace(
            "GiftTable.asset", ""
        )
        try:
            components = parse_exported_file(path)
            main_component = components[0]["MonoBehaviour"]

            for gift_level in list(GiftLevel):
                try:
                    gift_table = parse_gift_section(
                        indexer, main_component, gift_level, gift_table
                    )
                except:
                    logging.error(
                        "Could not get %s gifts for %s",
                        gift_level.value,
                        path,
                        exc_info=True,
                    )
                    pprint.pprint(main_component)

            for i in range(0, len(main_component["birthdayResponses"])):
                if i == 0:
                    gift_table.disliked.birthday_reponse = main_component[
                        "birthdayResponses"
                    ][i]
                elif i == 1:
                    gift_table.liked.birthday_response = main_component[
                        "birthdayResponses"
                    ][i]
                elif i == 2:
                    gift_table.loved.birthday_response = main_component[
                        "birthdayResponses"
                    ][i]

            if report_progress is not None:
                report_progress()
            tables.append(gift_table)
        except:
            logging.error("Couldn't parse %s", path, exc_info=True)

    return tables
