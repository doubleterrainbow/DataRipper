"""All methods used to convert skill and skill tree assets to Skill and SkillTree objects"""
import logging
import pprint
from DesktopApp.asset_ripper_parser.exported_file_parser import parse_exported_file
from DesktopApp.asset_ripper_parser.index_files import FileIndexer
from DesktopApp.asset_ripper_parser.parse_sprite_sheet import (
    Sprite,
    parse_sprite_asset,
)
from DesktopApp.asset_ripper_parser.utils import camel_case_split


class Skill:
    """Stores data relevant to a skill in-game"""

    def __init__(self):
        self.name = ""
        self.title = ""
        self.description = ""
        self.points = 1
        self.sprite = Sprite()

    def __str__(self):
        result = []

        result.append(f"{self.title} ({self.name})")
        result.append(f"\t{self.description}")
        result.append(f"\t{str(self.sprite)}")

        return "\n".join(result)


class SkillTree:
    """Stores data relevant to a skill tree in-game"""

    def __init__(self):
        self.name = ""
        self.skills: list[Skill] = []

    def __str__(self):
        return self.name + "\n" + "\n\n".join([str(skill) for skill in self.skills])


def parse_skills(
    indexer: FileIndexer, all_skill_paths: list[str], relevant_skill_paths: list[str]
) -> list[Skill]:
    """
    Returns a list of skills within a given list of paths
    """
    skills = []
    for item in relevant_skill_paths:
        skill_filepath = indexer.find_filepath_from_guid(item["guid"])
        if skill_filepath is not None:
            skill_components = parse_exported_file(skill_filepath)
            skill_component = skill_components[0]["MonoBehaviour"]

            skill = Skill()
            skill.name = skill_component["nodeName"]
            skill.title = skill_component["nodeTitle"]
            skill.points = skill_component["nodePoints"]
            skill.description = skill_component["description"]

            skill_sprite_path = indexer.find_sprite_path_from_guid(
                skill_component["icon"]["guid"]
            )
            if skill_sprite_path is not None:
                skill.sprite = parse_sprite_asset(indexer, skill_sprite_path)

            skill.description = replace_placeholders_in_description(
                skill_component, skill.description
            )

            skills.append(skill)
    return skills


def replace_placeholders_in_description(skill_component: dict, description: str) -> str:
    """Given a description, replace placeholder texts with the correct amounts.

    Args:
        skill_component (dict): data from skill asset file
        description (str): skill description

    Returns:
        str: description with placeholders replaced, or original description if an exception occurred.
    """
    try:
        updated_description = description
        if "ITEM1" in description:
            updated_description = description.replace(
                "ITEM1", str(skill_component["descriptionItems"][0])
            )

        if "ITEM2" in description:
            updated_description = description.replace(
                "ITEM2", str(skill_component["descriptionItems"][1])
            )

        if "ITEM3" in description:
            updated_description = description.replace(
                "ITEM3", str(skill_component["descriptionItems"][2])
            )

        if "ITEM4" in description:
            updated_description = description.replace(
                "ITEM4",
                str(skill_component["backupdescriptionItems"][0]),
            )

        if "ITEM5" in description:
            updated_description = description.replace(
                "ITEM5",
                str(skill_component["backupdescriptionItems"][1]),
            )

        if "ITEM6" in description:
            updated_description = description.replace(
                "ITEM6",
                str(skill_component["backupdescriptionItems"][2]),
            )

        if "UNLOCK" in description:
            updated_description = description.replace(
                "UNLOCK",
                str(skill_component["singleDescriptionItem"]),
            )

        return updated_description
    except:
        logging.error(
            f"Unable to populate description placeholders for %s",
            description,
            exc_info=True,
        )
        return description


def parse_skill_trees(
    indexer: FileIndexer,
    filepaths: list[str],
    skill_filepaths: list[str],
    report_progress=None,
) -> list[SkillTree]:
    """Using list of skill tree filepaths and skill filepaths,
    creates a list of SkillTree objects containing Skill objects

    Args:
        indexer (FileIndexer): used for looking up file paths and file names
        filepaths (list[str]): list of skill tree asset file paths
        skill_filepaths (list[str]): list of skill asset file paths
        report_progress (function, optional): Called after each item has been parsed. Defaults to None.

    Returns:
        list[SkillTree]: List of SkillTree objects containing data from asset files
    """
    trees = []
    for path in filepaths:
        tree = SkillTree()
        tree.name = camel_case_split(path.split("\\")[-1].replace(".asset", ""))
        try:
            components = parse_exported_file(path)
            main_component = components[0]["MonoBehaviour"]
            try:
                referenced_skills = main_component["serializationData"][
                    "ReferencedUnityObjects"
                ]

                skills = parse_skills(indexer, skill_filepaths, referenced_skills)

                if report_progress is not None:
                    report_progress()

                tree.skills = skills
                trees.append(tree)
            except:
                pprint.pprint(main_component)
                logging.error("Couldn't parse %s", tree.name, exc_info=True)
        except:
            logging.error("Couldn't parse %s", path, exc_info=True)

    return trees
