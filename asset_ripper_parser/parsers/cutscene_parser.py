"""All methods used to parse GiftTables."""
import logging
import os
import pprint
import re
from asset_ripper_parser.exported_file_parser import parse_exported_file
from asset_ripper_parser.index_files import FileIndexer
from asset_ripper_parser.models.cutscene import Cutscene, CutsceneDialogue
from asset_ripper_parser.models.quest import BulletinBoardQuest, Quest
from asset_ripper_parser.models.recipe import Ingredient
from asset_ripper_parser.utils import camel_case_split


def clean_text(text):
    """Removes junk from text, like italic formatting characters and colors.

    Args:
        text (str): dialogue from game.

    Returns:
        str: dialogue more usable on the wiki.
    """
    return text.replace("XX", "{{PLAYER}}").replace("[]", "<br>")


def parse_cutscene(path: str):
    filename = os.path.basename(path)
    cutscene = Cutscene(camel_case_split(filename.replace(".cs", "")))
    with open(path, "r", encoding="utf-8") as cutscene_file:
        # dialogues = []
        # npc = None
        # for line in cutscene_file.readlines():
        #     # print("line: ", line)
        #     if re.search(r"NPC\.\w+\.Name", line) is not None:
        #         npc = line.split("\"", 2)[1]
        #     if re.search(r"Cutscene\.\w+\.Option", line) is not None:
        #         dialogues.append("> " + line.split("\"", 2)[1])
        #     if re.search(r"Cutscene\.\w+\.Dialogue", line) is not None:
        #         if npc is None:
        #             npc = camel_case_split(filename).split(" ", 1)[0]
        #         dialogues.append(f"{npc}: " + line.split("\"", 2)[1])

        code = cutscene_file.read()

        # Define data structure to hold dialogue information
        dialogue_data = []

        dialogue_code = code.split("SceneRoutine()", 2)[1]
        dialogue_code = dialogue_code.split("this.Complete();", 1)[0]

        npc_marker = r"(?:DialogueController\.Instance\.SetDialogueBustVisuals\(this\.|DialogueController\.Instance\.SetDefaultBox\(\(string\)TranslationLayer\.TranslateObject\(\")"
        for talking_npc in re.split(npc_marker, dialogue_code):
            npc = re.split(r"[\"\.]", talking_npc, maxsplit=1)[0].capitalize()

            # Extract dialogue parts using regular expressions
            dialogue_pattern = r"base\.(?:DialogueSingle|DialogueSingleNoResponse)\((?:\(string\)TranslationLayer\.TranslateObject\()?\"(.*?)\", ([\w\s\d;\/\"?.,<>\[\]\(\)\=\{\}'\-!]*?)(?:false|true)\);"
            dialogue_matches = re.findall(dialogue_pattern, talking_npc, re.DOTALL)

            print(f"{len(dialogue_matches)} dialogues when talking to {npc}")
            for match in dialogue_matches:
                dialogue_text = clean_text(match[0].strip())
                options_args = match[1].strip()

                single_options_pattern = r'new ValueTuple<string, UnityAction>\(.*?"(.*?)", "(.*?)"\), null\)'
                single_options_matches = re.findall(
                    single_options_pattern, options_args
                )

                options_data = []
                for option_match in single_options_matches:
                    option_text = option_match[0]

                    options_data.append({"text": option_text, "hearts": 0})

                # Extract options using regular expression
                options_pattern = r'new ValueTuple<string, UnityAction>\(.*?"(.*?)", ".*?"\), delegate\(\)[\s\{\}]*(?:response = \d;)?(?:this\.\w+\.AddRelationship\((-?\d)f, 0f\))?'
                options_matches = re.findall(options_pattern, options_args)

                for option_match in options_matches:
                    option_text = option_match[0]
                    pprint.pprint(option_match)
                    hearts = 0
                    if option_match[1] != "":
                        hearts = int(option_match[1])

                    options_data.append({"text": option_text, "hearts": hearts})

                dialogue_data.append(
                    {"npc": npc, "text": dialogue_text, "options": options_data}
                )

        cutscene.dialogues = dialogue_data

        # dialogue = CutsceneDialogue()
        # for line in cutscene_file.readlines():
        #     if "NPC." in line:
        #         dialogue.npc = line.split("\"", 2)[1]
        #         npc = dialogue.npc
        #     elif ".Option" in line:
        #         dialogue.options.append(line.split("\"", 2)[1])
        #     elif ".Dialogue" in line:
        #         dialogue.responses.append(line.split("\"", 2)[1])
        #     elif dialogue.npc is None:
        #         dialogue.npc = npc

    return cutscene


def parse_cutscenes(filepaths: list[str], report_progress=None):
    """Given a list of file paths, returns a list of Quest objects.

    Each file is opened and read for relevant data.

    Args:
        indexer (FileIndexer): used for file lookups
        filepaths (list[str]): file paths like <RNPC_NAME>GiftTable.asset
        report_progress (function, optional): Runs every time a gift table is parsed.
                                            Defaults to None.

    Returns:
        list[Cutscene]: parsed Cutscene objects containing data relevant to a cutscene
    """
    cutscenes = []
    for path in filepaths:
        try:
            cutscene = parse_cutscene(path)

            if report_progress is not None:
                report_progress()

            cutscenes.append(cutscene)
        except:
            logging.error("Couldn't parse %s", path, exc_info=True)

    return cutscenes
