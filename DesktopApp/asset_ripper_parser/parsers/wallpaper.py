


import logging
from DesktopApp.asset_ripper_parser.exported_file_parser import parse_exported_file
from DesktopApp.asset_ripper_parser.index_files import FileIndexer
from DesktopApp.asset_ripper_parser.parsers.furniture import Furniture


def parse_wallpaper(indexer: FileIndexer, items: list[str]):
    furnitures = []
    for path in items:
        furniture = Furniture()
        furniture.category = "Wallpaper"
        parsed_wallpaper = parse_exported_file(path)
        main_component = parsed_wallpaper[0]
        
        try:
            item_filename = indexer.find_filepath_from_guid(main_component[0]['_itemData']['guid'])
            item_filepath = [x for x in items if item_filename in x]
            
            if item_filepath:
                item = parse_exported_file(item_filepath[0])
                item_component = item[0]
                
                furniture.name = item_component['name'].strip()
                furniture.id = item_component['id']
                furniture.stack_size = item_component['stack']
                furniture.hearts = item_component['hearts']
                furniture.rarity = item_component['rarity']
                furniture.is_dlc = item_component['isDLCItem'] == 1
                
                if furniture['sellPrice'] > 0:
                    furniture.sells_for = furniture['sellPrice']
                    furniture.sell_type = "Coins"
                elif furniture['orbsSellPrice'] > 0:
                    furniture.sells_for = furniture['orbsSellPrice']
                    furniture.sell_type = "Orbs"
                elif furniture['ticketSellPrice'] > 0:
                    furniture.sells_for = furniture['ticketSellPrice']
                    furniture.sell_type = "Tickets"
                    
        except:
            logging.error(f"Could not parse item for {path}", exc_info=True)
            
        furnitures.append(furniture)
    return furnitures
            

