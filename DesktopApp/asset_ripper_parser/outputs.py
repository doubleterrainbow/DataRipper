"""Contains all functions that can intake list of asset filepaths and output human-friendly files"""
import logging
import os
from DesktopApp.asset_ripper_parser.parser_registry import ParserRegistry
from DesktopApp.asset_ripper_parser.parsers.furniture_parser import parse_furniture

from DesktopApp.asset_ripper_parser.parsers.gift_table_parser import parse_gift_tables
from DesktopApp.asset_ripper_parser.parsers.monsters import parse_monsters
from DesktopApp.asset_ripper_parser.parsers.recipe_parser import parse_recipes
from DesktopApp.asset_ripper_parser.parsers.skill_tree_parser import parse_skill_trees
from DesktopApp.asset_ripper_parser.parsers.wallpaper import parse_wallpaper
from DesktopApp.file_tags import FileTags


@ParserRegistry.include("Recipes", [FileTags.RecipeList])
def produce_recipes(file_indexer, report_progress, output_dir, files):
    """Generates a text file of {{Recipe}} wiki templates given a list of
    assets containing recipe references.

    Args:
        file_indexer (FileIndexer): used for looking up files from a GUID
        report_progress (function): callback to run after every item is parsed
        output_dir (str): path to directory where files will be written
        files (dict): dict with a list of paths to assets containing "craftingRecipes"
    """
    with open(
        os.path.join(output_dir, "recipe_templates.txt"), "w", encoding="utf-8"
    ) as output_file:
        recipe_list_files = files[FileTags.RecipeList.value]

        logging.debug("Found %d recipe lists", len(recipe_list_files))
        recipes = parse_recipes(file_indexer, recipe_list_files, report_progress)
        for recipe in recipes:
            output_file.write(str(recipe))
            output_file.write("\n\n")


@ParserRegistry.include("Skills", [FileTags.SkillTree])
def produce_skills(file_indexer, report_progress, output_dir, files):
    """Creates a text file with all skills given a list of skill tree assets.

    Args:
        file_indexer (FileIndexer): used for lookup up files from their GUID reference.
        report_progress (function): Called every time a skill tree has finished parsing
        output_dir (str): path to the directory where resulting files will be stored
        files (dict): contains a list of file paths to the skill tree assets
    """
    with open(
        os.path.join(output_dir, "skills.txt"), "w", encoding="utf-8"
    ) as output_file:
        skill_tree_files = files[FileTags.SkillTree.value]

        logging.debug("Found %d skill trees", len(skill_tree_files))
        skill_trees = parse_skill_trees(
            file_indexer, skill_tree_files, report_progress=report_progress
        )
        for skill_tree in skill_trees:
            output_file.write(str(skill_tree))
            output_file.write("\n\n")


@ParserRegistry.include("Gift Tables", [FileTags.GiftTable])
def produce_gift_tables(file_indexer, report_progress, output_dir, files):
    """Create a text file containing readable gift tables for RNPCS.

    Args:
        file_indexer (FileIndexer): used for file lookups
        report_progress (function): callback to notify that an item has been processed.
        output_dir (str): file path for the folder to put the resulting text files.
        files (dict): file paths organized by FileTags
    """
    with open(
        os.path.join(output_dir, "gift_tables.txt"), "w", encoding="utf-8"
    ) as output_file:
        gift_table_files = files[FileTags.GiftTable.value]
        logging.debug("Found %d gift tables", len(gift_table_files))
        gift_tables = parse_gift_tables(file_indexer, gift_table_files, report_progress)

        for table in gift_tables:
            output_file.write(str(table))
            output_file.write("\n\n")


@ParserRegistry.include("Monsters", [FileTags.Enemy])
def produce_monsters(file_indexer, report_progress, output_dir, files):
    """Create a text file containing readable monster data from a
    list of assets.

    Args:
        file_indexer (FileIndexer): used for file lookups
        report_progress (function): callback to notify that an item has been processed.
        output_dir (str): file path for the folder to put the resulting text files.
        files (dict): file paths organized by FileTags
    """
    with open(
        os.path.join(output_dir, "monsters.txt"), "w", encoding="utf-8"
    ) as output_file:
        monster_files = files[FileTags.Enemy.value]

        logging.debug("Found %d monters", len(monster_files))
        monsters = parse_monsters(file_indexer, monster_files, report_progress)
        for monster in monsters:
            output_file.write(str(monster))
            output_file.write("\n\n")


@ParserRegistry.include("Furniture", [FileTags.Placeable])
def produce_furniture(file_indexer, report_progress, output_dir, files):
    """Creates 2 files,
    one more readable which describes furniture,
    and one with copy/paste wiki templates

    Args:
        file_indexer (FileIndexer): indexer for file lookups
        report_progress (function): function that increments progress bars
        output_dir (str): path of directory to place created files
        files (list[str]): list of file paths to parse
    """
    placeable_files = files[FileTags.Placeable.value]
    logging.debug("Found %s furniture items", len(placeable_files))
    furniture = parse_furniture(
        indexer=file_indexer,
        placeables=placeable_files,
        report_progress=report_progress,
    )

    with open(
        os.path.join(output_dir, "furniture.txt"), "w", encoding="utf-8"
    ) as output_file:
        for item in furniture:
            output_file.write(str(item))
            output_file.write("\n\n")

    with open(
        os.path.join(output_dir, "furniture_summaries.txt"), "w", encoding="utf-8"
    ) as output_file:
        for item in furniture:
            output_file.write(item.name + "\n")
            output_file.write(item.to_wiki_template())
            output_file.write("\n\n")


@ParserRegistry.include("Wallpaper", [FileTags.Wallpaper])
def produce_wallpaper(file_indexer, report_progress, output_dir, files):
    """Given a list of asset files, creates a text file containing details about wallpapers.

    Args:
        file_indexer (FileIndexer): used for file lookups
        report_progress (function): callback to notify that an item has been processed.
        output_dir (str): file path for the folder to put the resulting text files.
        files (dict): file paths organized by FileTags
    """
    with open(
        os.path.join(output_dir, "wallpaper.txt"), "w", encoding="utf-8"
    ) as output_file:
        wallpaper_files = files[FileTags.Wallpaper.value]
        logging.debug("Found %s wallpapers", len(wallpaper_files))
        wallpaper = parse_wallpaper(
            indexer=file_indexer, items=wallpaper_files, report_progress=report_progress
        )

        for item in wallpaper:
            output_file.write(str(item))
            output_file.write("\n\n")


included_parsers = ParserRegistry.registry
