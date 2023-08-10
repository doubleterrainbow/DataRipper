

import logging
import os
from DesktopApp.asset_ripper_parser.index_files import FileIndexer

from DesktopApp.asset_ripper_parser.parsers.gift_tables import parse_gift_tables
from DesktopApp.asset_ripper_parser.parsers.monsters import parse_monsters
from DesktopApp.asset_ripper_parser.parsers.parser_registry import ParserRegistry
from DesktopApp.asset_ripper_parser.parsers.recipes import parse_recipes
from DesktopApp.asset_ripper_parser.parsers.skill_tree import parse_skill_trees
from DesktopApp.file_tags import FileTags


@ParserRegistry.include("Recipes", [FileTags.Recipe, FileTags.RecipeList])
def produce_recipes(file_indexer, report_progress, output_dir, files):
    with open(os.path.join(output_dir, 'recipe_templates.txt'), 'w') as output_file:
        recipe_list_files = files[FileTags.RecipeList.value]
        recipe_files = files[FileTags.Recipe.value]
        
        logging.debug(f"Found {len(recipe_files)} recipes and {len(recipe_list_files)} recipe lists")
        recipes = parse_recipes(file_indexer, recipe_list_files, recipe_files, report_progress)
        for recipe in recipes:
            output_file.write(str(recipe))
            output_file.write("\n\n")

@ParserRegistry.include("Skills", [FileTags.SkillTree, FileTags.Skill])
def produce_skills(file_indexer, report_progress, output_dir, files):
    with open(os.path.join(output_dir, 'skills.txt'), 'w') as output_file:
        skill_tree_files = files[FileTags.SkillTree.value]
        skill_files = files[FileTags.Skill.value]
        
        logging.debug(f"Found {len(skill_tree_files)} skill trees")
        skill_trees = parse_skill_trees(file_indexer, skill_tree_files, skill_files, report_progress=report_progress)
        for skill_tree in skill_trees:
            output_file.write(str(skill_tree))
            output_file.write("\n\n")

@ParserRegistry.include("Gift Tables", [FileTags.GiftTable])
def produce_gift_tables(file_indexer, report_progress, output_dir, files):
    with open(os.path.join(output_dir, 'gift_tables.txt'), 'w') as output_file:
        gift_table_files = files[FileTags.GiftTable.value]
        logging.debug(f"Found {len(gift_table_files)} gift tables")
        gift_tables = parse_gift_tables(file_indexer, gift_table_files, report_progress)
        
        for table in gift_tables:
            output_file.write(str(table))
            output_file.write("\n\n")
            
@ParserRegistry.include("Monsters", [FileTags.Enemy])
def produce_monsters(file_indexer, report_progress, output_dir, files):
    with open(os.path.join(output_dir, 'monsters.txt'), 'w') as output_file:
        monster_files = files[FileTags.Enemy.value]
        
        logging.debug(f"Found {len(monster_files)} monters")
        monsters = parse_monsters(file_indexer, monster_files, report_progress)
        for monster in monsters:
            output_file.write(str(monster))
            output_file.write("\n\n")

included_parsers = ParserRegistry.registry

