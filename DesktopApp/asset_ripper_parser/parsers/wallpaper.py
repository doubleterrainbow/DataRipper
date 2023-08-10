"""All functions related to converting wallpaper asset files into Furniture objects."""
import logging
from DesktopApp.asset_ripper_parser.exported_file_parser import parse_exported_file
from DesktopApp.asset_ripper_parser.index_files import FileIndexer
from DesktopApp.asset_ripper_parser.parsers.furniture import Furniture
from DesktopApp.asset_ripper_parser.parse_sprite_sheet import parse_sprite_asset


def parse_wallpaper(indexer: FileIndexer, items: list[str], report_progress = None) -> list[Furniture]:
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
            item_component = parse_exported_file(path)[0]['MonoBehaviour']
            
            furniture.name = item_component["name"].strip()
            furniture.id = item_component["id"]
            furniture.stack_size = item_component["stackSize"]
            furniture.hearts = item_component["hearts"]
            furniture.rarity = item_component["rarity"]
            furniture.is_dlc = item_component["isDLCItem"] == 1
            
            sprite_path = indexer.find_sprite_path_from_guid(item_component['wallpaper']['guid'])
            furniture.sprite = parse_sprite_asset(indexer, sprite_path)

            if item_component["sellPrice"] > 0:
                furniture.sells_for = item_component["sellPrice"]
                furniture.sell_type = "Coins"
            elif item_component["orbsSellPrice"] > 0:
                furniture.sells_for = item_component["orbsSellPrice"]
                furniture.sell_type = "Orbs"
            elif item_component["ticketSellPrice"] > 0:
                furniture.sells_for = item_component["ticketSellPrice"]
                furniture.sell_type = "Tickets"
        except:
            logging.error("Could not parse item for %s", path, exc_info=True)

        if report_progress is not None:
            report_progress()

        furnitures.append(furniture)
    return furnitures
