


import logging
from DesktopApp.asset_ripper_parser.exported_file_parser import parse_exported_file
from DesktopApp.asset_ripper_parser.index_files import FileIndexer

class Furniture:
    def __init__(self):
        self.name = ""
        self.id = 0
        self.stack_size = 1
        self.category = "Misc"
        self.placed_on = "floor"
        self.sells_for = 0
        self.sell_type = "Coins"
        self.rarity = 0
        self.hearts = 1
        self.is_dlc = False


def parse_furniture(indexer: FileIndexer, items: list[str], decorations: list[str], placeables: list[str]):
    furnitures = []
    for path in placeables:
        furniture = Furniture()
        parsed_furniture = parse_exported_file(path)
        main_component = [comp for comp in parsed_furniture if '_decoration' in comp]
        
        try:
            decoration_filename = indexer.find_filepath_from_guid(main_component[0]['_decoration']['guid'])
            decoration_filepath = [x for x in decorations if decoration_filename in x]
            
            if decoration_filepath:
                decoration = parse_exported_file(decoration_filepath[0])
                decoration_component = [comp for comp in decoration if 'placeableOnTables' in comp]
        
                if decoration_component[0]["placeableOnTables"] != 0:
                    furniture.placed_on = "surface"
                elif decoration_component[0]["placeableOnWalls"] != 0:
                    furniture.placed_on = "wall"
                else:
                    furniture.placed_on = "floor"
                    
                if decoration_component[0]["placeableAsRug"] != 0:
                    furniture.category = "Rug"
        
        except:
            logging.error(f"Could not parse decoration for {path}", exc_info=True)
        
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
            

