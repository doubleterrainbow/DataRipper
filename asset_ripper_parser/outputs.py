"""Contains all functions that can intake list of asset file paths and output human-friendly files"""
import csv
import itertools
import logging
import os
from asset_ripper_parser.file_tags import FileTagLabel
from asset_ripper_parser.models.item import Item
from asset_ripper_parser.models.rnpc import RNPC
from asset_ripper_parser.parser_registry import ParserRegistry
from asset_ripper_parser.parsers.barn_animal_parser import parse_barn_animals
from asset_ripper_parser.parsers.bundle_parser import parse_bundles
from asset_ripper_parser.parsers.clothing_parser import parse_clothing
from asset_ripper_parser.parsers.cutscene_parser import parse_cutscenes
from asset_ripper_parser.parsers.fish_spawn_parser import parse_fish_spawners
from asset_ripper_parser.parsers.furniture_parser import parse_furniture

from asset_ripper_parser.parsers.gift_table_parser import parse_gift_tables
from asset_ripper_parser.parsers.item_parser import (
    parse_items,
    produce_description_template,
    produce_description_module,
)
from asset_ripper_parser.parsers.memory_potion_parser import (
    parse_memory_loss_potion_responses,
)
from asset_ripper_parser.parsers.monster_parser import parse_monsters
from asset_ripper_parser.parsers.monster_spawn_parser import (
    parse_monster_spawns,
)
from asset_ripper_parser.parsers.quest_parser import parse_bulletin_quests, parse_quests
from asset_ripper_parser.parsers.recipe_parser import parse_recipes, parse_skill_tomes
from asset_ripper_parser.parsers.rnpc_parser import parse_rnpcs
from asset_ripper_parser.parsers.shop_parser import (
    parse_merchants,
)
from asset_ripper_parser.parsers.skill_tree_parser import parse_skill_trees
from asset_ripper_parser.parsers.wallpaper_parser import parse_wallpaper
from asset_ripper_parser.utils import clean_text


@ParserRegistry.include("Barn Animals", [FileTagLabel.BARN_ANIMAL])
def produce_barn_animals(indexer, report_progress, output_dir, files):
    """TODO

    Args:
        indexer (FileIndexer): used for file lookups
        report_progress (function): callback to notify that an item has been processed.
        output_dir (str): file path for the folder to put the resulting text files.
        files (dict): file paths organized by FileTags
    """
    with open(
        os.path.join(output_dir, "barn_animals.txt"), "w", encoding="utf-8"
    ) as output_file:
        animal_files = [x for x in files[FileTagLabel.BARN_ANIMAL] if ".unity" not in x]
        logging.debug("Found %d barn animals", len(animal_files))
        animals = parse_barn_animals(indexer, animal_files, report_progress)
        for animal in animals:
            output_file.write(str(animal))
            output_file.write("\n\n")


@ParserRegistry.include("Bulletin Quests", [FileTagLabel.BULLETIN_BOARD])
def produce_bulletin_quests(indexer, report_progress, output_dir, files):
    """TODO

    Args:
        indexer (FileIndexer): used for file lookups
        report_progress (function): callback to notify that an item has been processed.
        output_dir (str): file path for the folder to put the resulting text files.
        files (dict): file paths organized by FileTags
    """
    with open(
        os.path.join(output_dir, "bulletin_quests.txt"), "w", encoding="utf-8"
    ) as output_file:
        quest_files = files[FileTagLabel.BULLETIN_BOARD]

        logging.debug("Found %d bulletins", len(quest_files))
        quests = parse_bulletin_quests(indexer, quest_files, report_progress)
        for quest in quests:
            output_file.write(str(quest))
            output_file.write("\n")
            output_file.write(quest.to_wiki_tags())
            output_file.write("\n\n")


@ParserRegistry.include("Bundles", [FileTagLabel.BUNDLE])
def produce_bundles(file_indexer, report_progress, output_dir, files):
    """Create a text file containing readable monster data from a
    list of assets.

    Args:
        file_indexer (FileIndexer): used for file lookups
        report_progress (function): callback to notify that an item has been processed.
        output_dir (str): file path for the folder to put the resulting text files.
        files (dict): file paths organized by FileTags
    """
    with open(
        os.path.join(output_dir, "bundles.txt"), "w", encoding="utf-8"
    ) as output_file:
        bundle_files = [x for x in files[FileTagLabel.BUNDLE] if ".unity" not in x]

        logging.debug("Found %d bundles", len(bundle_files))
        bundles = parse_bundles(file_indexer, bundle_files, report_progress)
        for bundle in bundles:
            output_file.write(str(bundle))
            output_file.write("\n\n")


def write_npc_file(output_dir: str, destination: str, npc: RNPC):
    with open(
        os.path.join(output_dir, destination), "w", encoding="utf-8"
    ) as output_file:
        try:
            output_file.write(npc.walk_cycles_to_wiki_tags())
            output_file.write("\n\n")
        except:
            logging.error("Error writing %s walk cycles", npc.name, exc_info=True)

        if npc.gift_table.loved:
            output_file.write(str(npc.gift_table))

        if npc.married_gifts:
            output_file.write("\n\n===Gifts For the Player===")
            output_file.write("\n{{GiftsForPlayer|\n")
            for gift in npc.married_gifts:
                output_file.write(
                    f",{gift.item_name}*{gift.amount}:[[{npc.name}/Dialogue#Morning Gifts|Morning Gift]]"
                )
            output_file.write("\n}}")
            output_file.write("\n\n")

            output_file.write(npc.married_gifts_to_wiki_tags())
            output_file.write("\n\n")

        try:
            output_file.write(npc.one_liners_to_wiki_tags())
            output_file.write("\n\n")
        except:
            logging.error("Error writing %s one liners", npc.name, exc_info=True)

        try:
            output_file.write(npc.dialogue_cycles_to_wiki_tags())
            output_file.write("\n\n")
        except:
            logging.error("Error writing %s dialogue cycles", npc.name, exc_info=True)

        try:
            output_file.write(
                "<br>This page details out the mail the player receives from '''[[{{BASEPAGENAME}}]]'''. Once "
                "specific relationship levels are reached, {{BASEPAGENAME}} will send gifts in the mail which "
                "can be collected from the farm's mailbox.\n"
            )
            for mail in npc.mail:
                output_file.write(mail.to_wiki_tags())
                output_file.write("\n\n")
        except:
            logging.error("Error writing %s mail", npc.name, exc_info=True)


@ParserRegistry.include(
    "RNPCS", [FileTagLabel.RNPC, FileTagLabel.MAIL, FileTagLabel.QUEST]
)
def produce_rnpcs(file_indexer, report_progress, output_dir, files):
    """Create a text file containing readable monster data from a
    list of assets.

    Args:
        file_indexer (FileIndexer): used for file lookups
        report_progress (function): callback to notify that an item has been processed.
        output_dir (str): file path for the folder to put the resulting text files.
        files (dict): file paths organized by FileTags
    """

    rnpc_files = [x for x in files[FileTagLabel.RNPC] if ".unity" not in x]

    logging.debug("Found %d romanceable npcs", len(rnpc_files))
    os.makedirs(os.path.join(output_dir, "rnpcs"), exist_ok=True)

    parse_rnpcs(
        file_indexer,
        rnpc_files,
        files[FileTagLabel.MAIL],
        files[FileTagLabel.QUEST],
        report_progress,
        on_npc_completed=(
            lambda npc: write_npc_file(output_dir, f"rnpcs/{npc.name}.txt", npc)
        ),
    )


@ParserRegistry.include("NPCS", [FileTagLabel.NPC, FileTagLabel.MAIL])
def produce_npcs(file_indexer, report_progress, output_dir, files):
    """Create a text file containing readable monster data from a
    list of assets.

    Args:
        file_indexer (FileIndexer): used for file lookups
        report_progress (function): callback to notify that an item has been processed.
        output_dir (str): file path for the folder to put the resulting text files.
        files (dict): file paths organized by FileTags
    """

    npc_files = [x for x in files[FileTagLabel.NPC] if ".unity" not in x]

    logging.debug("Found %d npcs", len(npc_files))
    os.makedirs(os.path.join(output_dir, "npcs"), exist_ok=True)

    parse_rnpcs(
        file_indexer,
        npc_files,
        files[FileTagLabel.MAIL],
        [],
        report_progress,
        on_npc_completed=(
            lambda npc: write_npc_file(output_dir, f"npcs/{npc.name}.txt", npc)
        ),
    )


@ParserRegistry.include("Quests", [FileTagLabel.QUEST])
def produce_quests(indexer, report_progress, output_dir, files):
    """TODO

    Args:
        indexer (FileIndexer): usedf for file lookups
        report_progress (function): callback to notify that an item has been processed.
        output_dir (str): file path for the folder to put the resulting text files.
        files (dict): file paths organized by FileTags
    """
    with open(
        os.path.join(output_dir, "quests.txt"), "w", encoding="utf-8"
    ) as output_file:
        quest_files = [x for x in files[FileTagLabel.QUEST] if ".unity" not in x]

        logging.debug("Found %d quests", len(quest_files))
        quests = parse_quests(indexer, quest_files, report_progress)
        for quest in quests:
            output_file.write(str(quest))
            output_file.write("\n")
            output_file.write(quest.to_wiki_tags())
            output_file.write("\n\n")


@ParserRegistry.include("Recipes", [FileTagLabel.RECIPE_LIST])
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
        recipe_list_files = files[FileTagLabel.RECIPE_LIST]

        logging.debug("Found %d recipe lists", len(recipe_list_files))
        recipes = parse_recipes(file_indexer, recipe_list_files, report_progress)
        for recipe in recipes:
            output_file.write(str(recipe))
            output_file.write("\n\n")


@ParserRegistry.include("Skill Tome Recipes", [FileTagLabel.SKILL_TOME])
def produce_skill_tome_recipes(file_indexer, report_progress, output_dir, files):
    """Generates a text file of {{Recipe}} wiki templates given a list of
    assets containing recipe references.

    Args:
        file_indexer (FileIndexer): used for looking up files from a GUID
        report_progress (function): callback to run after every item is parsed
        output_dir (str): path to directory where files will be written
        files (dict): dict with a list of paths to assets containing "craftingRecipes"
    """
    with open(
        os.path.join(output_dir, "recipe_skill_tome_templates.txt"),
        "w",
        encoding="utf-8",
    ) as output_file:
        recipe_files = files[FileTagLabel.SKILL_TOME]

        logging.debug("Found %d skill tome recipes", len(recipe_files))
        recipes = parse_skill_tomes(file_indexer, recipe_files, report_progress)
        for recipe in recipes:
            output_file.write(str(recipe))
            output_file.write("\n\n")


def write_item_file(output_dir, batch_number, items: list[Item]):
    with open(
        os.path.join(output_dir, f"items_{batch_number}.csv"), "w", encoding="utf-8"
    ) as output_file:
        csv_writer = csv.writer(output_file)
        for item in items:
            csv_writer.writerow(
                [
                    item.name,
                    item.sprite.name,
                    item.sprite.file_id,
                    item.sprite.x,
                    item.sprite.y,
                    item.sprite.height,
                    item.sprite.width,
                    item.sprite.image_path,
                ]
            )


@ParserRegistry.include("Items", [FileTagLabel.ITEM])
def produce_items(file_indexer, report_progress, output_dir, files):
    """Generates a text file of item info given a list of
    assets containing item references.

    Args:
        file_indexer (FileIndexer): used for looking up files from a GUID
        report_progress (function): callback to run after every item is parsed
        output_dir (str): path to directory where files will be written
        files (dict): dict with a list of asset paths
    """
    item_files = files[FileTagLabel.ITEM]

    logging.debug("Found %d items", len(item_files))

    def write_to_file(batch, _, parsed_items):
        # write_item_file(output_dir, batch, parsed_items)
        # with open(
        #     os.path.join(output_dir, "item_names.txt"), "w", encoding="utf-8"
        # ) as item_name_file:
        #     for item in parsed_items:
        #         item_name_file.write(f"{item.name}\n")

        # with open(
        #     os.path.join(output_dir, "description_template.txt"), "w", encoding="utf-8"
        # ) as description_file:
        #     description_file.write(produce_description_template(parsed_items))
        with open(
            os.path.join(output_dir, "description_module.txt"), "w", encoding="utf-8"
        ) as description_file:
            description_file.write(produce_description_module(parsed_items))

        with open(
            os.path.join(output_dir, "items_infoboxes.txt"), "w", encoding="utf-8"
        ) as output_file:
            for item in parsed_items:
                output_file.write(item.to_wiki_tags())
                output_file.write("\n\n")

    parse_items(
        file_indexer,
        item_files,
        batch_size=8000,
        on_batch_complete=write_to_file,
        report_progress=report_progress,
        parse_sprite=True,
    )

    #
    # with open(
    #     os.path.join(output_dir, "missing_descriptions.txt"), "w", encoding="utf-8"
    # ) as description_file:
    #     for item in items:
    #         if item.description == "":
    #             description_file.write(f"{item.name}\n")


@ParserRegistry.include("Clothes", [FileTagLabel.CLOTHING])
def produce_clothes(file_indexer, report_progress, output_dir, files):
    """Generates a text file of item info given a list of
    assets containing item references.

    Args:
        file_indexer (FileIndexer): used for looking up files from a GUID
        report_progress (function): callback to run after every item is parsed
        output_dir (str): path to directory where files will be written
        files (dict): dict with a list of asset paths
    """
    clothing_files = files[FileTagLabel.CLOTHING]

    logging.debug("Found %d clothes", len(files[FileTagLabel.CLOTHING]))

    def write_to_file(batch, _, parsed_items):
        with open(
            os.path.join(output_dir, f"clothes_{batch}.csv"), "w", encoding="utf-8"
        ) as output_file:
            csv_writer = csv.writer(output_file)
            for clothes in parsed_items:
                csv_writer.writerow(clothes.to_list())

    parse_clothing(
        file_indexer,
        clothing_files,
        batch_size=500,
        on_batch_complete=write_to_file,
        report_progress=report_progress,
    )


@ParserRegistry.include("MerchantTables", [FileTagLabel.MERCHANT_TABLE])
def produce_merchants(file_indexer, report_progress, output_dir, files):
    """Generates a text file of shop info given a list of
    assets containing shop references.

    Args:
        file_indexer (FileIndexer): used for looking up files from a GUID
        report_progress (function): callback to run after every shop is parsed
        output_dir (str): path to directory where files will be written
        files (dict): dict with a list of asset paths
    """
    merchant_files = files[FileTagLabel.MERCHANT_TABLE]
    shops = parse_merchants(file_indexer, merchant_files, report_progress)
    with open(
        os.path.join(output_dir, "merchant_tables.txt"), "w", encoding="utf-8"
    ) as output_file:
        logging.debug("Found %d shops", len(merchant_files))
        for shop in shops:
            output_file.write(str(shop))
            output_file.write("\n\n")

    with open(
        os.path.join(output_dir, "merchant_tables_templates.txt"), "w", encoding="utf-8"
    ) as output_file:
        for shop in shops:
            output_file.write(shop.to_wiki_tags())
            output_file.write("\n\n")


@ParserRegistry.include("Skills", [FileTagLabel.SKILL_TREE])
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
        skill_tree_files = files[FileTagLabel.SKILL_TREE]

        logging.debug("Found %d skill trees", len(skill_tree_files))
        skill_trees = parse_skill_trees(
            file_indexer, skill_tree_files, report_progress=report_progress
        )
        for skill_tree in skill_trees:
            output_file.write(str(skill_tree))
            output_file.write("\n\n")


@ParserRegistry.include("Gift Tables", [FileTagLabel.GIFT_TABLE])
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
        gift_table_files = files[FileTagLabel.GIFT_TABLE]
        logging.debug("Found %d gift tables", len(gift_table_files))
        gift_tables = parse_gift_tables(file_indexer, gift_table_files, report_progress)

        for table in gift_tables:
            output_file.write(table.npc_name + "\n")
            output_file.write(str(table))
            output_file.write("\n\n")


@ParserRegistry.include("Monsters", [FileTagLabel.ENEMY])
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
        monster_files = files[FileTagLabel.ENEMY]

        logging.debug("Found %d monters", len(monster_files))
        monsters = parse_monsters(file_indexer, monster_files, report_progress)
        for monster in monsters:
            output_file.write(str(monster))
            output_file.write("\n\n")


@ParserRegistry.include("MonsterSpawns", [FileTagLabel.SCENE, FileTagLabel.ENEMY])
def produce_monster_spawns(_, report_progress, output_dir, files):
    """Create a text file containing readable monster data from a
    list of assets.

    Args:
        _ (FileIndexer): not needed for this function
        report_progress (function): callback to notify that an item has been processed.
        output_dir (str): file path for the folder to put the resulting text files.
        files (dict): file paths organized by FileTags
    """
    with open(
        os.path.join(output_dir, "monster_spawns.txt"), "w", encoding="utf-8"
    ) as output_file:
        scene_files = files[FileTagLabel.SCENE]
        enemy_files = files[FileTagLabel.ENEMY]

        logging.debug("Found %d scenes", len(scene_files))
        locations = parse_monster_spawns(scene_files, enemy_files, report_progress)
        for location in locations:
            output_file.write(str(location))
            output_file.write("\n\n")


@ParserRegistry.include("Furniture", [FileTagLabel.PLACEABLE])
def produce_furniture(file_indexer, report_progress, output_dir, files):
    """Creates 2 files,
    one more readable which describes furniture,
    and one with copy/paste wiki templates

    Args:
        file_indexer (FileIndexer): indexer for file lookups
        report_progress (function): function that increments progress bars
        output_dir (str): path of directory to place created text
        files (dict): map of {FileTagLabel: list[str]} with filepaths to parse
    """
    placeable_files = files[FileTagLabel.PLACEABLE]
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


@ParserRegistry.include("Wallpaper", [FileTagLabel.WALLPAPER])
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
        wallpaper_files = files[FileTagLabel.WALLPAPER]
        logging.debug("Found %s wallpapers", len(wallpaper_files))
        wallpaper = parse_wallpaper(
            indexer=file_indexer, items=wallpaper_files, report_progress=report_progress
        )

        for item in wallpaper:
            output_file.write(str(item))
            output_file.write("\n\n")


@ParserRegistry.include("Fish Spawners", [FileTagLabel.FISH_SPAWNER])
def produce_fish_spawners(file_indexer, report_progress, output_dir, files):
    """Given a list of asset files, creates a text file containing details about wallpapers.

    Args:
        file_indexer (FileIndexer): used for file lookups
        report_progress (function): callback to notify that an item has been processed.
        output_dir (str): file path for the folder to put the resulting text files.
        files (dict): file paths organized by FileTags
    """
    with open(
        os.path.join(output_dir, "fish_spawners.txt"), "w", encoding="utf-8"
    ) as output_file:
        spawner_files = files[FileTagLabel.FISH_SPAWNER]
        logging.debug("Found %s fish spawn locations", len(spawner_files))
        fish_spawns = parse_fish_spawners(file_indexer, spawner_files, report_progress)

        fish_spawns_grouped = {}
        for spawner in fish_spawns:
            for drop in spawner.drops:
                if drop.item.name not in fish_spawns_grouped:
                    fish_spawns_grouped[drop.item.name] = []
                fish_spawns_grouped[drop.item.name].append(drop)

            for drop in spawner.spring_drops:
                if drop.item.name not in fish_spawns_grouped:
                    fish_spawns_grouped[drop.item.name] = []
                fish_spawns_grouped[drop.item.name].append(drop)

            for drop in spawner.summer_drops:
                if drop.item.name not in fish_spawns_grouped:
                    fish_spawns_grouped[drop.item.name] = []
                fish_spawns_grouped[drop.item.name].append(drop)

            for drop in spawner.fall_drops:
                if drop.item.name not in fish_spawns_grouped:
                    fish_spawns_grouped[drop.item.name] = []
                fish_spawns_grouped[drop.item.name].append(drop)

            for drop in spawner.winter_drops:
                if drop.item.name not in fish_spawns_grouped:
                    fish_spawns_grouped[drop.item.name] = []
                fish_spawns_grouped[drop.item.name].append(drop)

        for key, value in fish_spawns_grouped.items():
            output_file.write(str(key) + "\n")
            output_file.write("\n".join([str(x) for x in set(value)]))
            output_file.write("\n\n")


def produce_cutscenes(cutscene_files: list[str], report_progress, output_dir):
    logging.debug("Found %s cutscenes", len(cutscene_files))
    cutscenes = parse_cutscenes(cutscene_files, report_progress=report_progress)
    with open(
        os.path.join(output_dir, "cutscene_event_scenes.txt"), "w", encoding="utf-8"
    ) as output_file:
        for scene in cutscenes:
            output_file.write(scene.to_wiki_tags())
            output_file.write("\n\n")

    with open(
        os.path.join(output_dir, "cutscene_names.txt"), "w", encoding="utf-8"
    ) as cutscene_name_file:
        for scene in cutscenes:
            cutscene_name_file.write(f"{scene.name}\n")

    # with open(
    #     os.path.join(output_dir, "cutscenes.txt"), "w", encoding="utf-8"
    # ) as output_file:
    #     for scene in cutscenes:
    #         output_file.write(str(scene))
    #         output_file.write("\n\n")
    #
    # with open(
    #     os.path.join(output_dir, "cutscene_tables.txt"), "w", encoding="utf-8"
    # ) as output_file:
    #     for scene in cutscenes:
    #         output_file.write(scene.to_wiki_tags(template="Table"))
    #         output_file.write("\n\n")


def produce_memory_loss_potion_lines(
    npc_ai_file: list[str], report_progress, output_dir
):
    logging.debug("Parsing memory loss potion dialogues")
    responses = parse_memory_loss_potion_responses(
        npc_ai_file, report_progress=report_progress
    )
    with open(
        os.path.join(output_dir, "memory_loss_potion_responses.txt"),
        "w",
        encoding="utf-8",
    ) as output_file:
        for response in responses:
            output_file.write(str(response))
            output_file.write("\n\n")


included_parsers = ParserRegistry.registry
