"""Main file for running this app without getting bogged down by TkInter.
Runs purely on the command line.
"""
import csv
import logging
import os

import inquirer
from alive_progress import alive_bar
from asset_ripper_parser.outputs import (
    included_parsers,
    produce_cutscenes,
    produce_memory_loss_potion_lines,
)
from asset_ripper_parser.index_files import FileIndexer
from inquirer import errors, Text, Checkbox, Path, themes


def setup(
    asset_dir: str,
    output_dir: str,
    tagged_files: str,
    create_ids: bool,
    categorize_files: bool,
) -> FileIndexer:
    file_indexer = FileIndexer(
        assets_folder=asset_dir,
        ids_file=os.path.join(output_dir, "file_mappings", "ids.csv"),
        file_tags_file=tagged_files,
    )

    file_count = file_indexer.get_asset_count()

    if create_ids:
        with alive_bar(file_count) as progress_bar:

            def report_map_progress():
                # pylint: disable=not-callable
                progress_bar(1000)
                progress_bar.text("Storing file IDs")

            file_indexer.create_mapping_files(
                report_progress=report_map_progress,
            )

    subdir_count = len([x[0] for x in os.walk(file_indexer.assets_folder)])
    if categorize_files:
        with alive_bar(subdir_count) as progress_bar:

            def report_org_progress():
                # pylint: disable=not-callable
                progress_bar()
                progress_bar.text(f"{subdir_count} folders: determining file types")

            file_indexer.create_organization_file(
                report_progress=report_org_progress,
            )

    return file_indexer


def interactive_setup():
    questions = [
        Text(
            "Asset Directory",
            message="What folder are the assets in?",
        ),
        Text(
            "Code Directory",
            message="What folder is the code in?",
        ),
        Text(
            "Output Directory",
            message="What folder should the resulting files be placed in? (does not need to exist)",
        ),
        inquirer.List(
            "first_run",
            message="Is this your first time running with these assets?",
            choices=["yes", "no"],
            default="yes",
        ),
        Checkbox(
            "outputs",
            message="What outputs should be created? (press spacebar to select)",
            choices=[
                "Barn Animals",
                "Bundles",
                "Bulletin Quests",
                "Clothes",
                "Fish Spawners",
                "Items",
                "MerchantTables",
                "Monsters",
                "Shops",
                "Quests",
                "Recipes",
                "RNPCS",
                "NPCS",
                "Cutscenes",
                "Memory Potion Dialogues",
            ],
            default=["Items"],
        ),
    ]

    answers = inquirer.prompt(questions)
    parse_data(answers)


def parse_data(settings):
    """Parses assets and sorting data into more readable outputs."""
    # asset_dir = "D:\\Documents\\Sun Haven Assets\\AssetRipperExport_1.2.2"
    # code_dir = "D:\\Documents\\Sun Haven Assets\\Code_1.2.2\\SunHaven.Core"
    # output_dir = "D:\\Documents\\Sun Haven Assets\\test_output_1.2.2"

    # Asset ripper export folder
    asset_dir = settings["Asset Directory"].replace('"', "")

    # DNSpy output folder
    code_dir = settings["Code Directory"].replace('"', "") + "\\SunHaven.Core"

    # Resulting Files will be here
    output_dir = settings["Output Directory"].replace('"', "")

    # Skips indexing and tagging files
    categorize_files = settings["first_run"] == "yes"
    create_ids = settings["first_run"] == "yes"
    parse_cutscenes = "Cutscenes" in settings["outputs"]
    parse_memory_loss_potion_lines = "Memory Potion Dialogues" in settings["outputs"]

    tagged_files = os.path.join(output_dir, "file_mappings", "tagged_files.csv")

    os.makedirs(os.path.join(output_dir, "file_mappings"), exist_ok=True)

    # Bar Styles
    # 'smooth', 'classic', 'classic2', 'brackets', 'blocks',
    # 'bubbles', 'solid', 'checks', 'circles', 'squares', 'halloween',
    # 'filling', 'notes', 'ruler', 'ruler2', 'fish', 'scuba'

    # Spinner Styles
    # 'classic', 'stars', 'twirl', 'twirls', 'horizontal', 'vertical',
    # 'waves', 'waves2', 'waves3', 'dots', 'dots_waves', 'dots_waves2',
    # 'it', 'ball_belt', 'balls_belt', 'triangles', 'brackets', 'bubbles',
    # 'circles', 'squares', 'flowers', 'elements', 'loving', 'notes',
    # 'notes2', 'arrow', 'arrows', 'arrows2', 'arrows_in', 'arrows_out',
    # 'radioactive', 'boat', 'fish', 'fish2', 'fishes', 'crab', 'alive',
    # 'wait', 'wait2', 'wait3', 'wait4', 'pulse'

    all_parsers = [
        # Parser Name, bar style (arbitrary), spinner style (arbitrary)
        ("Barn Animals", "checks", "fishes"),
        ("Bundles", "filling", "ball_belt"),
        ("Bulletin Quests", "bubbles", "loving"),
        ("Clothes", "brackets", "notes"),
        ("Fish Spawners", "fish", "fish2"),
        ("Furniture", "blocks", "dots"),
        ("Gift Tables", "checks", "loving"),
        ("Items", "bubbles", "fish2"),
        ("MerchantTables", "squares", "pulse"),
        ("Monsters", "halloween", "elements"),
        (
            "MonsterSpawns",
            "halloween",
            "twirl",
        ),  # This is a very slow step. Should be run on its own
        ("Shops", "squares", "flowers"),
        ("Quests", "bubbles", "loving"),
        ("Recipes", "circles", "dots"),
        ("RNPCS", "bubbles", "loving"),
        ("NPCS", "bubbles", "ball_belt"),
        ("Skill Tome Recipes", "circles", "dots"),
        ("Skills", "blocks", "elements"),
        ("Wallpaper", "blocks", "elements"),
    ]

    enabled_parsers = [x for x in all_parsers if x[0] in settings["outputs"]]

    file_indexer = setup(
        asset_dir=asset_dir,
        output_dir=output_dir,
        tagged_files=tagged_files,
        create_ids=create_ids,
        categorize_files=categorize_files,
    )

    with open(tagged_files, "r", encoding="utf-8") as tagged_files:
        file_tag_reader = csv.reader(tagged_files)
        file_tags = list(file_tag_reader)

        parsers = included_parsers
        for parser in parsers:
            matching_parser = [x for x in enabled_parsers if parser.label == x[0]]
            if matching_parser:
                files = {}
                for tag in parser.tags:
                    files[tag] = [line[0] for line in file_tags if tag.value in line]

                try:
                    primary_file_amount = len(next(iter(files.values())))
                    with alive_bar(
                        primary_file_amount,
                        bar=matching_parser[0][1],
                        spinner=matching_parser[0][2],
                    ) as parser_bar:

                        def report_progress(text=None):
                            # pylint: disable=not-callable,cell-var-from-loop
                            parser_bar()
                            if text is not None:
                                parser_bar.text(text)
                            else:
                                parser_bar.text(parser.label)

                        parser.func_callable(
                            file_indexer, report_progress, output_dir, files
                        )
                except:
                    logging.error("Error when linking %s", parser.label, exc_info=True)

        if parse_cutscenes:
            cutscene_files = [
                os.path.join(dir_path, file)
                for dir_path, _, file_names in os.walk(code_dir)
                for file in file_names
                if "Cutscene" in file
            ]
            with alive_bar(len(cutscene_files)) as cutscene_bar:

                def report_cutscene_progress():
                    # pylint: disable=not-callable,cell-var-from-loop
                    cutscene_bar()
                    cutscene_bar.text("Cutscenes")

                # filtered_cutscenes = [x for x in cutscene_files if "hello" in x]
                produce_cutscenes(cutscene_files, report_cutscene_progress, output_dir)

        if parse_memory_loss_potion_lines:
            npc_ai_file = [
                os.path.join(dir_path, file)
                for dir_path, _, file_names in os.walk(code_dir)
                for file in file_names
                if file.endswith("NPCAI.cs")
            ]
            with alive_bar(len(npc_ai_file)) as potion_bar:

                def report_potion_progress():
                    # pylint: disable=not-callable,cell-var-from-loop
                    potion_bar()
                    potion_bar.text("Memory Loss Potion Texts")

                produce_memory_loss_potion_lines(
                    npc_ai_file, report_potion_progress, output_dir
                )
    print("Done!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    interactive_setup()
