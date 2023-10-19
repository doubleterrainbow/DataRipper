import logging
import os
import re

from asset_ripper_parser.index_files import FileIndexer
from asset_ripper_parser.models.recipe import Ingredient
from asset_ripper_parser.models.rnpc import (
    RNPC,
    OneLiner,
    RelationshipLevel,
    Dialogue,
    DialogueCycle,
    WalkCycle,
    WalkPath,
    MarriedGift,
)
from asset_ripper_parser.models.season import Season
from asset_ripper_parser.parse_exported_file import parse_exported_file
from asset_ripper_parser.parsers.gift_table_parser import parse_gift_tables
from asset_ripper_parser.parsers.mail_parser import parse_mail
from asset_ripper_parser.parsers.quest_parser import parse_quests
from asset_ripper_parser.utils import camel_case_to_words


def clean_text(text):
    """Replace in-game markers with wiki markers. Notably, line breaks
    and player name.

    Args:
        text (str): dialogue from game.

    Returns:
        str: dialogue more usable on the wiki.
    """
    return text.replace("XX", "{{PLAYER}}").replace("[]", "<br>")


def get_season_from_world_progress(indexer: FileIndexer, tokens: list[dict]):
    season = Season.ANY
    for requirement in tokens:
        progress = indexer.find_name_from_guid(requirement["guid"])
        if progress in ["Spring", "Summer", "Fall", "Winter"]:
            season = [x for x in list(Season) if x.name.lower() == progress.lower()][0]

    return season


def parse_cycle(indexer: FileIndexer, dialogue_cycle: dict, npc_name: str):
    if "guid" not in dialogue_cycle["text"]:
        return None

    cycle = DialogueCycle()
    text_file = indexer.find_filepath_from_guid(dialogue_cycle["text"]["guid"])

    with open(text_file, "r", encoding="utf-8") as dialogue_file:
        try:
            for line in dialogue_file.readlines():
                if line == "" or "::" not in line:
                    cycle_number = re.search(r"Cycle P?(\d+)\.txt", text_file)
                    if cycle_number is not None:
                        cycle.number = int(cycle_number.group(1))
                    continue

                dialogue = Dialogue()
                dialogue.text = clean_text(line.split("::")[1].strip())
                dialogue.is_response = line.startswith("Response")

                if line.startswith("Option"):
                    dialogue.number = int(re.search(r"Option(\d+)\w?::", line).group(1))
                    subsection = re.search(r"Option\d+(\w)+::", line)
                    if subsection is not None:
                        dialogue.sub_letter = subsection.group(1)

                if line.startswith("Response"):
                    dialogue.number = int(
                        re.match(r"Response(\d+)\w?::", line).group(1)
                    )
                    subsection = re.search(r"Response\d+(\w)+::", line)
                    if subsection is not None:
                        dialogue.sub_letter = subsection.group(1)

                cycle.dialogue.append(dialogue)
        except:
            logging.error(
                "Couldn't parse cycle %d, file %s",
                cycle.number,
                text_file,
                exc_info=True,
            )
    return cycle


def parse_dialogue_cycles(indexer: FileIndexer, component: dict, rnpc: RNPC) -> RNPC:
    for line in component["_oneLiners"]:
        season = get_season_from_world_progress(indexer, line["worldProgressTokens"])

        relationship_level = RelationshipLevel.STRANGERS
        for requirement in line["characterProgressTokens"]:
            if "guid" in requirement:
                progress = indexer.find_name_from_guid(requirement["guid"])
                if "Cycle" in progress:
                    relationship_level = RelationshipLevel.FRIENDS
                elif "Dating" in progress:
                    relationship_level = RelationshipLevel.DATING
                elif "Married" in progress:
                    relationship_level = RelationshipLevel.MARRIAGE

        for text in line["text"]:
            one_liner = OneLiner()
            one_liner.season = season
            one_liner.level = relationship_level
            if "guid" in text:
                text_file = indexer.find_filepath_from_guid(text["guid"])
                with open(text_file, "r", encoding="utf-8") as dialogue_file:
                    dialogue = dialogue_file.read()
                    one_liner.text = clean_text(
                        dialogue.split("Dialogue::")[1].replace("\n\nEnd", "")
                    ).strip()

                rnpc.one_liners.append(one_liner)

    for dialogue_cycle in component["_dialogueCycles"]:
        cycle = parse_cycle(indexer, dialogue_cycle, rnpc.name)
        if cycle is not None:
            cycle.level = RelationshipLevel.STRANGERS
            rnpc.dialogues.append(cycle)

    for dialogue_cycle in component["_datingCycles"]:
        cycle = parse_cycle(indexer, dialogue_cycle, rnpc.name)
        if cycle is not None:
            cycle.level = RelationshipLevel.DATING
            rnpc.dialogues.append(cycle)

    for dialogue_cycle in component["_platonicCycles"]:
        cycle = parse_cycle(indexer, dialogue_cycle, rnpc.name)
        if cycle is not None:
            cycle.level = RelationshipLevel.FRIENDS
            rnpc.dialogues.append(cycle)

    for dialogue_cycle in component["_marriedCycles"]:
        cycle = parse_cycle(indexer, dialogue_cycle, rnpc.name)
        if cycle is not None:
            cycle.level = RelationshipLevel.MARRIAGE
            rnpc.dialogues.append(cycle)

    return rnpc


def parse_walk_cycles(indexer: FileIndexer, walk_cycle_path: str):
    cycles = []
    component = parse_exported_file(walk_cycle_path)[0]["MonoBehaviour"]
    for walk_path in component["npcPaths"]:
        walk_cycle = WalkCycle()
        walk_path_file = indexer.find_filepath_from_guid(walk_path["guid"])
        walk_cycle.path_name = camel_case_to_words(
            os.path.basename(walk_path_file.replace(".asset", ""))
        ).strip()

        pathing_component = parse_exported_file(walk_path_file)[0]["MonoBehaviour"]
        requirements = []
        for requirement in pathing_component["worldProgressTokens"]:
            progress = indexer.find_name_from_guid(requirement["guid"])
            if "Married" in progress:
                requirements.append("Married")
            else:
                requirements.append(camel_case_to_words(progress))
        for requirement in pathing_component["characterProgressTokens"]:
            requirement_file = indexer.find_name_from_guid(requirement["guid"])
            requirements.append(camel_case_to_words(requirement_file))
        walk_cycle.requirements = requirements

        for path in pathing_component["paths"]:
            walk_path = WalkPath(path["name"], path["hour"])
            walk_cycle.paths.append(walk_path)

        cycles.append(walk_cycle)
    return cycles


def parse_rnpcs(
    indexer: FileIndexer,
    paths: list[str],
    mail_paths: list[str],
    quest_paths: list[str],
    report_progress=None,
    on_npc_completed=None,
) -> list[RNPC]:
    """
    Given a list of asset file paths, return a list of Recipe objects containing relevant data.
    File paths should be recipe lists, meaning they contain the "craftingRecipes" attribute. This
    allows us to provide a workbench name with each recipe output.

    Args:
        indexer (FileIndexer): used for file lookup from GUIDs
        paths (list[str]): each path refers to a recipe list asset file
        mail_paths (list[str]): each path refers to every possible piece of mail in the game.
        report_progress (function, optional): Runs every time a recipe list is parsed.
                                              Defaults to None.

    Returns:
        list[RNPC]: the recipes used in asset files, in Recipe objects.
    """
    rnpcs = []
    for path in paths:
        try:
            components = [
                comp
                for comp in parse_exported_file(path)
                if "MonoBehaviour" in comp and "walkCycle" in comp["MonoBehaviour"]
            ]
            main_component = components[0]["MonoBehaviour"]

            rnpc = RNPC(main_component["_npcName"])

            # # Parse Gift Table
            if "giftTable" in main_component and "guid" in main_component["giftTable"]:
                gift_table_file = indexer.find_filepath_from_guid(
                    main_component["giftTable"]["guid"]
                )
                gift_table = parse_gift_tables(indexer, [gift_table_file])
                rnpc.gift_table = gift_table[0]

            # Parse Walk Cycles
            if "guid" in main_component["walkCycle"]:
                default_walk_cycle_file = indexer.find_filepath_from_guid(
                    main_component["walkCycle"]["guid"]
                )
                default_walk_cycle = parse_walk_cycles(indexer, default_walk_cycle_file)
                rnpc.walk_cycles += default_walk_cycle

                for walk_cycle in main_component["seasonalWalkCycle"]:
                    filepath = indexer.find_filepath_from_guid(walk_cycle["guid"])
                    cycles = parse_walk_cycles(indexer, filepath)
                    rnpc.walk_cycles += cycles

            # Parse Mail
            relevant_mail = [x for x in mail_paths if rnpc.name in x]
            rnpc.mail = [
                x for x in parse_mail(indexer, relevant_mail) if x.npc_name == rnpc.name
            ]

            # Parse Married Gifts
            try:
                relevant_quests = [
                    x for x in quest_paths if f"{rnpc.name.strip()}Marri" in x
                ]
                for quest_path in relevant_quests:
                    quest_components = parse_exported_file(quest_path)
                    gift_component = quest_components[0]["MonoBehaviour"][
                        "giveItemsOnComplete"
                    ]
                    for gift_item in gift_component:
                        if "item" in gift_item and "guid" in gift_item["item"]:
                            rnpc.married_gifts.append(
                                MarriedGift(
                                    name=indexer.find_name_from_guid(
                                        gift_item["item"]["guid"]
                                    ),
                                    amount=gift_item["amount"],
                                    dialogue=quest_components[0]["MonoBehaviour"][
                                        "endTex"
                                    ],
                                )
                            )
            except:
                logging.error("Could not parse gifts for %s", rnpc.name, exc_info=True)

            # Parse Dialogue Cycles & One-Liners
            rnpc = parse_dialogue_cycles(indexer, main_component, rnpc)

            rnpcs.append(rnpc)

            if report_progress is not None:
                report_progress(f"Finished {rnpc.name}")

            if on_npc_completed is not None:
                on_npc_completed(rnpc)
        except:
            logging.error("Couldn't parse %s", path, exc_info=True)

    return rnpcs
