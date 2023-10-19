import re

from asset_ripper_parser.utils import camel_case_split


def apply_tags(text: str, npc_name) -> str:
    return remove_emote(add_item(add_quest(add_heart_points(text, npc_name), npc_name)))


def add_heart_points(text: str, npc_name) -> str:
    heart_points = re.search(
        r"//Relationship\s?" + re.escape(npc_name) + r"P?\d*[ab]? (-?\d)",
        text,
    )
    if heart_points is not None:
        points = int(heart_points.group(1))
        prefix = "+"
        if points < 0:
            prefix = "-"
        return (
            text.split("//", 1)[0]
            + " {{"
            + f"Heart Points|{prefix}|{abs(points)}"
            + "}}"
        )
    return text


def add_quest(text: str, npc_name: str) -> str:
    quest_name = re.search(
        r"//Quest \w+ (\S+)",
        text,
    )
    if quest_name is not None:
        split_name = ""
        if "Hangout2" in quest_name.group(1):
            split_name = "Date"
        elif "Hangout1" in quest_name.group(1):
            split_name = "Hangout Event"
        return (
            text.split("//", 1)[0]
            + " <span style=\"color: #710193;\">'''Quest:"
            + f"[[{npc_name}/Events#{split_name}|{split_name}]]"
            + "'''</span>"
        )
    return text


def add_item(text: str) -> str:
    item_name = re.search(
        r"//AddItem \w+ (\S+)",
        text,
    )
    if item_name is not None:
        item = re.sub(r"([A-Z])", " \\1", item_name.group(1))
        return (
            text.split("//", 1)[0]
            + " <span style=\"color: #dc2626;\">'''+ {{il|"
            + item.strip()
            + "}}'''</span>"
        )
    return text


def remove_emote(text: str) -> str:
    if "//Emote" in text:
        return text.split("//", 1)[0]
    return text
