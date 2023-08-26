"""All methods used to parse GiftTables."""
import logging
import re
from asset_ripper_parser.exported_file_parser import parse_exported_file
from asset_ripper_parser.index_files import FileIndexer
from asset_ripper_parser.models.quest import BulletinBoardQuest, Quest
from asset_ripper_parser.models.recipe import Ingredient


def clean_text(text):
    """Removes junk from text, like italic formatting characters and colors.

    Args:
        text (str): dialogue from game.

    Returns:
        str: dialogue more usable on the wiki.
    """
    result = text.replace("<i>", "''").replace("</i>", "''").replace("</color>", "")
    return re.sub(r"<color=#[0-9A-Z]+>", "", result)


def parse_quest(indexer: FileIndexer, main_component: dict):
    quest = Quest()

    quest.name = main_component["questName"]
    quest.short_description = main_component["overrideTurnInText"]

    if (
        "questDescription" in main_component
        and main_component["questDescription"] is not None
    ):
        quest.description = clean_text(main_component["questDescription"])

    quest.days = main_component["daysToDo"]
    quest.turn_in_to_npc = main_component["npcToTurnInTo"]
    quest.repeatable = main_component["repeatable"] > 0

    if "endTex" in main_component and main_component["endTex"] is not None:
        quest.turn_in_text = clean_text(main_component["endTex"])

    for requirement in main_component["itemRequirements"]:
        for item in requirement["items"]:
            required_item_name = indexer.find_name_from_guid(item["item"]["guid"])
            required_item = Ingredient()
            required_item.name = required_item_name
            required_item.amount = item["amount"]
            quest.requires.append(required_item)

    for item in main_component["guaranteeRewards"]:
        rewarded_item_name = indexer.find_name_from_guid(item["item"]["guid"])
        rewarded_item = Ingredient()
        rewarded_item.name = rewarded_item_name
        rewarded_item.amount = item["amount"]
        quest.rewards.append(rewarded_item)

    for item in main_component["choiceRewards"]:
        rewarded_item_name = indexer.find_name_from_guid(item["item"]["guid"])
        rewarded_item = Ingredient()
        rewarded_item.name = rewarded_item_name
        rewarded_item.amount = item["amount"]
        quest.bonus_rewards.append(rewarded_item)

    if isinstance(main_component["questProgressRequirements"], list):
        for progress in main_component["questProgressRequirements"]:
            if "guid" in progress:
                name = indexer.find_name_from_guid(progress["guid"]).replace(
                    ".asset", ""
                )
                quest.progress_requirements.append(name)
            elif "progressName" in progress:
                name = progress["progressName"]
                quest.progress_requirements.append(name)

    if isinstance(main_component["characterProgressRequirements"], list):
        quest.progress_requirements += [
            indexer.find_name_from_guid(x["guid"]).replace(".asset", "")
            for x in main_component["characterProgressRequirements"]
        ]

    if isinstance(main_component["worldProgressRequirements"], list):
        quest.progress_requirements += [
            indexer.find_name_from_guid(x["guid"]).replace(".asset", "")
            for x in main_component["worldProgressRequirements"]
        ]

    return quest


def parse_bulletin_quest(indexer: FileIndexer, path: str, report_progress=None):
    quest = BulletinBoardQuest()
    components = parse_exported_file(path)
    main_component = components[0]["MonoBehaviour"]

    quest.name = main_component["questName"]
    quest.short_description = main_component["overrideTurnInText"]
    quest.description = clean_text(main_component["questDescription"])
    quest.bulletin_board_description = clean_text(
        main_component["bulletinBoardDescription"]
    )
    quest.days = main_component["daysToDo"]
    quest.turn_in_to_npc = main_component["npcToTurnInTo"]
    quest.turn_in_text = main_component["endTex"]

    for requirement in main_component["itemRequirements"]:
        for item in requirement["items"]:
            required_item_name = indexer.find_name_from_guid(item["item"]["guid"])
            required_item = Ingredient()
            required_item.name = required_item_name
            required_item.amount = item["amount"]
            quest.requires.append(required_item)

    for item in main_component["guaranteeRewards"]:
        rewarded_item_name = indexer.find_name_from_guid(item["item"]["guid"])
        rewarded_item = Ingredient()
        rewarded_item.name = rewarded_item_name
        rewarded_item.amount = item["amount"]
        quest.rewards.append(rewarded_item)

    for item in main_component["choiceRewards"]:
        rewarded_item_name = indexer.find_name_from_guid(item["item"]["guid"])
        rewarded_item = Ingredient()
        rewarded_item.name = rewarded_item_name
        rewarded_item.amount = item["amount"]
        quest.bonus_rewards.append(rewarded_item)

    if isinstance(main_component["questProgressRequirements"], list):
        quest.progress_requirements += [
            indexer.find_name_from_guid(x["guid"]).replace(".asset", "")
            for x in main_component["questProgressRequirements"]
        ]

    if isinstance(main_component["characterProgressRequirements"], list):
        quest.progress_requirements += [
            indexer.find_name_from_guid(x["guid"]).replace(".asset", "")
            for x in main_component["characterProgressRequirements"]
        ]

    if isinstance(main_component["worldProgressRequirements"], list):
        quest.progress_requirements += [
            indexer.find_name_from_guid(x["guid"]).replace(".asset", "")
            for x in main_component["worldProgressRequirements"]
        ]

    if report_progress is not None:
        report_progress()

    return quest


def parse_bulletin_quests(
    indexer: FileIndexer, filepaths: list[str], report_progress=None
):
    """Given a list of file paths, returns a list of Quest objects.

    Each file is opened and read for relevant data.

    Args:
        indexer (FileIndexer): used for file lookups
        filepaths (list[str]): file paths containing bulletin board behaviours
        report_progress (function, optional): Runs every time a quest is parsed.
                                            Defaults to None.

    Returns:
        list[BulletinBoardQuest]: parsed BulletinBoardQuest objects
    """
    quests = []
    for path in filepaths:
        try:
            components = parse_exported_file(
                path, only_with_text="sunHavenBulletinBoardQuests"
            )
            main_component = components[0]["MonoBehaviour"]

            for ref in main_component["sunHavenBulletinBoardQuests"]:
                quest_path = indexer.find_filepath_from_guid(ref["guid"])
                quest = parse_bulletin_quest(indexer, quest_path, report_progress)
                quests.append(quest)

            for ref in main_component["withergateBulletinBoardQuests"]:
                quest_path = indexer.find_filepath_from_guid(ref["guid"])
                quest = parse_bulletin_quest(indexer, quest_path, report_progress)
                quests.append(quest)

            for ref in main_component["nelvariBulletinBoardQuests"]:
                quest_path = indexer.find_filepath_from_guid(ref["guid"])
                quest = parse_bulletin_quest(indexer, quest_path, report_progress)
                quests.append(quest)
        except:
            logging.error("Couldn't parse %s", path, exc_info=True)

    return quests


def parse_quests(indexer: FileIndexer, filepaths: list[str], report_progress=None):
    """Given a list of file paths, returns a list of Quest objects.

    Each file is opened and read for relevant data.

    Args:
        indexer (FileIndexer): used for file lookups
        filepaths (list[str]): file paths like <RNPC_NAME>GiftTable.asset
        report_progress (function, optional): Runs every time a gift table is parsed.
                                            Defaults to None.

    Returns:
        list[GiftTable]: parsed GiftTable objects containing data relevant to a RNPC
    """
    quests = []
    for path in filepaths:
        try:
            components = parse_exported_file(path)
            main_component = components[0]["MonoBehaviour"]

            quest = parse_quest(indexer, main_component)

            if report_progress is not None:
                report_progress()

            quests.append(quest)
        except:
            logging.error("Couldn't parse %s", path, exc_info=True)

    return quests
