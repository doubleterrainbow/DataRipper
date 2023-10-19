"""All methods used to parse GiftTables."""
import logging
import os
import pprint
import re

from asset_ripper_parser.models.memory_loss_potion_response import (
    MemoryLossPotionResponse,
)
from asset_ripper_parser.parse_exported_file import parse_exported_file
from asset_ripper_parser.index_files import FileIndexer
from asset_ripper_parser.models.cutscene import Cutscene, CutsceneDialogue
from asset_ripper_parser.models.quest import BulletinBoardQuest, Quest
from asset_ripper_parser.models.recipe import Ingredient
from asset_ripper_parser.utils import camel_case_split


def clean_text(text):
    """Replace in-game markers with wiki markers. Notably, line breaks
    and player name.

    Args:
        text (str): dialogue from game.

    Returns:
        str: dialogue more usable on the wiki.
    """
    return text.replace("XX", "{{PLAYER}}").replace("[]", "<br>")


def parse_memory_loss_responses(path: str):
    with open(path, "r", encoding="utf-8") as npc_ai_file:
        code = npc_ai_file.read()

        responses = []

        dialogue_code = code.split("private string HandleMemoryLossPotion", 2)[1]
        dialogue_code = dialogue_code.split("private string GetGiftResponse", 1)[0]

        npc_marker = r'if \(npcname == "(\w+)"\)\s*\{\s*return \(string\)TranslationLayer.TranslateObject\("(.+)",'
        response_matches = re.findall(npc_marker, dialogue_code)
        for match in response_matches:
            existing_response = [x for x in responses if x.npc_name == match[0]]
            if existing_response:
                response = existing_response[0]
            else:
                response = MemoryLossPotionResponse()
                response.npc_name = match[0]

            response_parts = re.split(
                r"\[]<i>\w+ drinks the potion... and forgets everything about your \w+!</i>\[]",
                match[1],
            )
            is_marriage_response = "forgets everything about your marriage!" in match[1]
            if is_marriage_response:
                response.initial_response = clean_text(response_parts[0])
                response.married_response = clean_text(response_parts[1])
            else:
                response.initial_response = clean_text(response_parts[0])
                response.platonic_response = clean_text(response_parts[1])

            if not existing_response:
                responses.append(response)

    return responses


def parse_memory_loss_potion_responses(
    filepaths: list[str], report_progress=None
) -> list[MemoryLossPotionResponse]:
    """Given a list of file paths, returns a list of cutscene objects.

    Each file is opened and read for relevant data.

    Args:
        filepaths (list[str]): file paths like <CUTSCENE_NAME>Cutscene.cs
        report_progress (function, optional): Runs every time a gift table is parsed.
                                            Defaults to None.

    Returns:
        list[Cutscene]: parsed Cutscene objects containing data relevant to a cutscene
    """
    responses = []
    for path in filepaths:
        try:
            responses = parse_memory_loss_responses(path)

            if report_progress is not None:
                report_progress()

        except:
            logging.error("Couldn't parse %s", path, exc_info=True)

    return responses
