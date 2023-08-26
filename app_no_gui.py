"""Main file for running this app without getting bogged down by TkInter. 
Runs purely on the command line.
"""
import csv
import logging
import os
import pprint
from alive_progress import alive_bar
from asset_ripper_parser.outputs import included_parsers, produce_cutscenes
from asset_ripper_parser.index_files import FileIndexer


def setup(
    asset_dir: str,
    output_dir: str,
    tagged_files: list,
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


def parse_data():
    """Parses assets and sorting data into more readable outputs."""
    # Asset ripper folder
    asset_dir = "D:\\Documents\\Sun Haven Assets\\AssetRipperExport_1.2.2"

    code_dir = "D:\\Documents\\Sun Haven Assets\\Code_1.2.2\\SunHaven.Core"

    # Output folder
    output_dir = "D:\\Documents\\Sun Haven Assets\\test_output_1.2.2"

    # Skips indexing and tagging files
    categorize_files = False
    create_ids = False
    parse_cutscenes = False

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

    enabled_parsers = [
        # Parser Name, bar style (arbitrary), spinner style (arbitrary)
        # ('Recipes', 'circles', 'dots'),
        ("Skill Tome Recipes", "circles", "dots"),
        # ('Skills', 'blocks', 'elements'),
        # ('Furniture', 'blocks', 'dots'),
        # ('Items', 'bubbles', 'fish2'),
        # ('Clothes', 'brackets', 'notes'),
        # ('Wallpaper', 'blocks', 'elements'),
        # ('MerchantTables', 'squares', 'pulse'),
        # ('Monsters', 'halloween', 'elements'),
        # ('MonsterSpawns', 'halloween', 'twirl'),
        # ('Shops', 'squares', 'flowers'),
        # ('Gift Tables', 'checks', 'loving'),
        # ('Quests', 'bubbles', 'loving'),
        # ('Bulletin Quests', 'bubbles', 'loving'),
    ]

    file_indexer = setup(
        asset_dir=asset_dir,
        output_dir=output_dir,
        tagged_files=tagged_files,
        create_ids=create_ids,
        categorize_files=categorize_files,
    )

    with open(tagged_files, "r", encoding="utf-8") as tagged_files:
        file_tags = csv.reader(tagged_files)

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

                        def report_progress():
                            # pylint: disable=not-callable,cell-var-from-loop
                            parser_bar()
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

                filtered_cutscenes = [x for x in cutscene_files if "Vivi" in x]
                produce_cutscenes(
                    filtered_cutscenes, report_cutscene_progress, output_dir
                )
    print("Done!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parse_data()
