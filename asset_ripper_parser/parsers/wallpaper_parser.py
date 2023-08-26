"""All functions related to converting wallpaper asset files into Furniture objects."""
import logging
from asset_ripper_parser.exported_file_parser import parse_exported_file
from asset_ripper_parser.index_files import FileIndexer
from asset_ripper_parser.parsers.furniture_parser import Furniture
from asset_ripper_parser.parsers.item_parser import parse_item


def parse_wallpaper(
    indexer: FileIndexer, items: list[str], report_progress=None
) -> list[Furniture]:
    """Given a list of asset file paths, return a list of Furniture objects.
    This function expects the item to have a "wallpaper" attribute.

    Args:
        indexer (FileIndexer): used to find filepaths and asset names
        items (list[str]): list of asset file paths, each representint a piece of wallpaper

    Returns:
        list[Furniture]: a list of Furniture objects containing wallpapers
    """
    furnitures = []
    for path in items:
        furniture = Furniture()
        furniture.category = "Wallpaper"
        furniture.placed_on = "wall"

        try:
            item_component = parse_exported_file(path)[0]["MonoBehaviour"]
            furniture = parse_item(
                indexer, item_component, furniture, item_component["wallpaper"]["guid"]
            )
        except:
            logging.error("Could not parse item for %s", path, exc_info=True)

        if report_progress is not None:
            report_progress()

        furnitures.append(furniture)
    return furnitures
