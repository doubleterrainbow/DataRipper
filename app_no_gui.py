"""Main file for running this app without getting bogged down by TkInter. 
Runs purely on the command line.
"""
import logging
import os
from alive_progress import alive_bar
from DesktopApp.asset_ripper_parser.outputs import included_parsers
from DesktopApp.asset_ripper_parser.index_files import FileIndexer

def parse_data():
    """Parses assets and sorting data into more readable outputs.
    """
    # Asset ripper folder
    asset_dir = "D:\\Documents\\Sun Haven Assets\\AssetRipperExport_1.2.2"

    # Output folder
    output_dir = "D:\\Documents\\Sun Haven Assets\\test_output_1.2.2"

    # Skips indexing and tagging files
    categorize_files = True
    create_ids = True

    tagged_files = os.path.join(output_dir, "file_mappings", "tagged_files.csv")

    os.makedirs(os.path.join(output_dir, "file_mappings"), exist_ok=True)

    # Bar Styles
    # 'smooth', 'classic', 'classic2', 'brackets', 'blocks',
    # 'bubbles', 'solid', 'checks', 'circles', 'squares', 'halloween',
    # 'filling', 'notes', 'ruler', 'ruler2', 'fish', 'scuba'

    enabled_parsers = [
        # Parser Name, bar style (arbitrary), spinner style (arbitrary)
        # ('Monsters', 'halloween', 'elements'),
        # ('Recipes', 'circles', 'dots'),
        ('Skills', 'blocks', 'elements'),
        # ('Furniture', 'blocks', 'dots'),
        ('Wallpaper', 'blocks', 'elements'),
        ('Gift Tables', 'checks', 'loving'),
    ]


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

    if categorize_files:
        with alive_bar(file_count) as progress_bar:
            def report_org_progress():
                # pylint: disable=not-callable
                progress_bar(1000)
                progress_bar.text("Tagging files")

            file_indexer.create_organization_file(
                report_progress=report_org_progress,
            )


    with open(tagged_files, 'r', encoding="utf-8") as tagged_files:
        file_tags = tagged_files.readlines()

        parsers = included_parsers
        for parser in parsers:
            matching_parser = [x for x in enabled_parsers if parser.label == x[0]]
            if matching_parser:
                files = {}
                for tag in parser.tags:
                    files[tag.value] = [line.split(',')[0] for line in file_tags
                                        if tag.value in line.strip().split(',')[1:] and "_0" not in line]

                try:
                    primary_file_amount = len(next(iter(files.values())))
                    with alive_bar(primary_file_amount,
                                   bar=matching_parser[0][1],
                                   spinner=matching_parser[0][2]
                                   ) as parser_bar:
                        def report_progress():
                            # pylint: disable=not-callable,cell-var-from-loop
                            parser_bar()
                            parser_bar.text(parser.label)

                        parser.callable(file_indexer, report_progress, output_dir, files)
                except Exception:
                    logging.error("Error when linking %s", parser.label, exc_info=True)

    print("Done!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    parse_data()