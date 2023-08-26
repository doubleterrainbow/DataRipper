# import os
# import re
# from asset_ripper_parser.index_files import FileIndexer
# from asset_ripper_parser.models.dialogue import Dialogue, DialogueLine
#
# def color_to_span(line: str) -> str:
#     return line.replace("<color=", '<span style="color: ').replace(
#         "</color>", "</span>"
#     )
#
#
# def replace_notes(line: str) -> str:
#     note = ""
#
#     green = "#3cb043"
#     red = "#dc2626"
#     quest = "#710193"
#     heart = "{{il|Heart|icon|size=14px}} Points"
#     relationship_marker = """<span style="color: {0};">'''{1}'''</span>"""
#
#     if "//Relationship" in line:
#         rString = line[line.index("//Relationship") :]
#         line = line[: -len(rString)].rstrip()
#         rTokens = rString.split(" ")
#         for v in rTokens:
#             try:
#                 note = " " + relationshipStr.format(
#                     green if int(v) > 0 else red,
#                     ("+" if int(v) > 0 else "") + v + " " + heart,
#                 )
#                 break
#             except ValueError:
#                 continue
#     elif "//Emote" in line:
#         rString = line[line.index("//Emote") :]
#         line = line[: -len(rString)].rstrip()
#     elif "//AddItem" in line:
#         rString = line[line.index("//AddItem") :]
#         line = line[: -len(rString)].rstrip()
#         rTokens = rString.split(" ")
#         note = " " + relationshipStr.format(red, "+ {{il|" + rTokens[2] + "}}")
#     elif "//Quest" in line:
#         rString = line[line.index("//Quest") :]
#         line = line[: -len(rString)].rstrip()
#         rTokens = rString.split(" ")
#         note = " " + relationshipStr.format(quest, "Quest: [[" + rTokens[2] + "]]")
#     elif "//Charon" in line:
#         line = line[: line.index("//Charon")].rstrip()
#     return (line + note).strip()
#
#
# def add_icons(filename: str) -> str:
#     season = None
#     if "Spring" in filename:
#         season = "icon_spring"
#     elif "Summer" in filename:
#         season = "icon_summer"
#     elif "Fall" in filename:
#         season = "icon_fall"
#     elif "Winter" in filename:
#         season = "icon_winter"
#
#     relationship = None
#     if "Dating" in filename:
#         relationship = "Love Letter"
#     elif "Married" in filename:
#         relationship = "Wedding Ring"
#
#     icons = ""
#     if relationship:
#         icons = " {{" + f"il|{relationship}|icon" + "}}"
#     if season:
#         icons += " {{{" + f"il|{season}|icon" + "}}"
#
#     return icons
#
#
# def parse_dialogues(
#     indexer: FileIndexer, paths: list[str], report_progress=None, parse_sprite=False
# ) -> list[str]:
#     """Given a list of file paths, returns a list of items.
#
#     Args:
#         indexer (FileIndexer):  used to look up the icon/sprite for this item.
#                                 Currently not doing that.
#         item_paths (list[str]): all asset file paths with item information.
#         report_progress (function, optional): Called when an item has been parsed. Defaults to None.
#         parse_sprite (bool): If true, will look up sprite and apply it to the returned object. Defaults to False.
#
#     Returns:
#         list[Item]: List of parsed items.
#     """
#     dialogues = []
#     for path in paths:
#         try:
#             with open(path, "r", encoding="utf-8") as dialogue_file:
#                 filename = os.path.basename(path).replace(".txt", "")
#
#                 title_parts = filename.split(" ")
#                 dialogue = Dialogue(
#                     npc=title_parts[0],
#                     cycle=int(title_parts[-1]),
#                     one_liner="One Liner" in filename,
#                 )
#
#                 current_line = DialogueLine()
#                 for line in dialogue_file.readlines():
#                     if line.startswith("Dialogue::"):
#                         current_line.dialogue = line.replace("Dialogue::").strip()
#                     elif line.startswith("Option"):
#                         current_line.options.append(
#                             re.sub(r"Option[0-9]+::", "", line).strip()
#                         )
#                     elif line.startswith("Response"):
#                         current_line.responses.append(
#                             re.sub(r"Response[0-9]+::", "", line).strip()
#                         )
#
#             if report_progress is not None:
#                 report_progress()
#             dialogues.append(item)
#         except:
#             logging.error("Could not parse %s", path, exc_info=True)
#     return dialogues
