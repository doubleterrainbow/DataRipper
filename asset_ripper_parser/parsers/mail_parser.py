import logging
import os

from asset_ripper_parser.index_files import FileIndexer
from asset_ripper_parser.models.mail import Mail
from asset_ripper_parser.models.recipe import Ingredient
from asset_ripper_parser.parse_exported_file import parse_exported_file
from asset_ripper_parser.utils import camel_case_to_words, clean_text


def parse_mail(indexer: FileIndexer, filepaths: list[str], report_progress=None):
    """Given a list of file paths, returns a list of Mail objects.

    Each file is opened and read for relevant data.

    Args:
        indexer (FileIndexer): used for file lookups
        filepaths (list[str]): file paths like <RNPC_NAME>GiftTable.asset
        report_progress (function, optional): Runs every time a gift table is parsed.
                                            Defaults to None.

    Returns:
        list[Mail]: parsed GiftTable objects containing data relevant to a RNPC
    """
    all_mail = []
    for path in filepaths:
        mail = Mail()
        try:
            components = parse_exported_file(path)
            main_component = components[0]["MonoBehaviour"]

            if "npcRelationship" in main_component:
                mail.npc_name = main_component["npcRelationship"]["NPCname"]
                mail.heart_level = main_component["npcRelationship"]["relationship"] / 5

            mail.message = clean_text(main_component["message"].replace("\n", "<br>"))

            if "items" in main_component:
                for item in main_component["items"]:
                    guid = item["item"]["guid"]
                    ingredient = Ingredient(
                        indexer.find_name_from_guid(guid), item["amount"]
                    )
                    mail.gifts.append(ingredient)

            for requirement in main_component["characterProgressIDs"]:
                if "guid" in requirement:
                    requirement_file = indexer.find_name_from_guid(requirement["guid"])
                    mail.progress.append(camel_case_to_words(requirement_file))

            for requirement in main_component["worldProgressIDs"]:
                if "guid" in requirement:
                    requirement_file = indexer.find_name_from_guid(requirement["guid"])
                    mail.progress.append(camel_case_to_words(requirement_file))

            all_mail.append(mail)
        except:
            logging.error("Couldn't parse %s", path, exc_info=True)

    return all_mail
