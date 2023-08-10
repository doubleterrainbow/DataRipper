

import logging
import pprint
from DesktopApp.asset_ripper_parser.exported_file_parser import parse_exported_file
from DesktopApp.asset_ripper_parser.index_files import FileIndexer

class Sprite:
    def __init__(self) -> None:
        self.name = ""
        self.file_id = 0
        self.x = 0
        self.y = 0
        self.height = 0
        self.width = 0
        self.image_path = ""
        
    def __str__(self):
        return f"{self.name},{self.x},{self.y},{self.width},{self.height},{self.image_path}"

def parse_sprite_sheet(filepath):
    """
    Unused
    """
    data = parse_exported_file(filepath)
    sprites = []
    
    for sprite in data['spriteSheet']['sprites']:
        parsed_sprite = Sprite()
        parsed_sprite.name = sprite['name'],
        parsed_sprite.file_id = sprite['internalID'],
        parsed_sprite.x = sprite['rect']['x'],
        parsed_sprite.y = sprite['rect']['y'],
        parsed_sprite.height = sprite['rect']['height'],
        parsed_sprite.width = sprite['rect']['width'],
        # 'gap': sprite['alignment'],
            
        sprites.append(parsed_sprite)
        
    return sprites
        
def parse_sprite_asset(indexer: FileIndexer, filepath: str):
    sprite = Sprite()
    parsed_file = parse_exported_file(filepath)
    data = parsed_file[0]['Sprite']
    try:
        
        sprite.name = data['m_Name']
        sprite.x = data['m_Rect']['x']
        sprite.y = data['m_Rect']['y']
        sprite.width = data['m_Rect']['width']
        sprite.height = data['m_Rect']['height']
        sprite.image_path = indexer.find_texture_path_from_guid(data['m_RD']['texture']['guid'])
        if sprite.image_path is None:
            sprite.image_path = data['m_RD']['texture']['guid']
    except:
        pprint.pprint(data)
        logging.error(f"Could not parse sprite {filepath}")
        
    return sprite
    