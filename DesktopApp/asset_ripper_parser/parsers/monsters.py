

from ast import List
from difflib import SequenceMatcher
from enum import Enum
import itertools
import logging
import pprint
import re
from DesktopApp.asset_ripper_parser.exported_file_parser import parse_exported_file
from DesktopApp.asset_ripper_parser.index_files import FileIndexer

class Monster:
    def __init__(self) -> None:
        self.name = ""
        self.health = 0
        self.experience = 0
        self.level = 0
        self.defense = 0
        self.min_damage = 0
        self.max_damage = 0
        self.ranged = False
        
        self.drops = []
        
    def __str__(self):
        result = [self.name + f" (level {self.level})"]

        result.append(f"Health: {self.health}")
        result.append(f"Experience: {self.experience}")
        result.append(f"Defense: {self.defense}")
        result.append(f"Damage: {self.min_damage}-{self.max_damage}")
        
        for drop in self.drops:
            for dropped_item in drop:
                if dropped_item['item'] is not None:
                    amount = str(dropped_item['amount_x'])
                    if dropped_item['amount_x'] != dropped_item['amount_y']:
                        amount += f"-{dropped_item['amount_y']}"
                    
                    result.append(f"\t{amount} {dropped_item['item']} ({round(dropped_item['percent_chance'], 2)}%)")
                
        return '\n'.join(result)
        
    def calculate_drop_percents(self):
        if not self.drops:
            return

        for group in self.drops:
            total_weight = sum([drop['chance'] for drop in group])
            
            for drop in group:
                drop['percent_chance'] = (drop['chance'] / total_weight) * 100 
    
def parse_monsters(indexer: FileIndexer, filepaths: list[str], report_progress=None):
    monsters = []
    for path in filepaths:
        monster = Monster()
        try:
            components = parse_exported_file(path)
            
            main_component = [comp for comp in components if 'MonoBehaviour' in comp and 'enemyName' in comp['MonoBehaviour']]
            damage_component = [comp for comp in components if 'MonoBehaviour' in comp and '_damageRange' in comp['MonoBehaviour']]
            try:
                monster_data = main_component[0]['MonoBehaviour']
                
                monster.name = monster_data['enemyName']
                monster.health = monster_data['_health']
                monster.experience = monster_data['_experience']
                monster.level = monster_data['_powerLevel']
                monster.defense = monster_data['defense']
                
                if damage_component:
                    monster.min_damage = damage_component[0]['MonoBehaviour']['_damageRange']['x']
                    monster.max_damage = damage_component[0]['MonoBehaviour']['_damageRange']['y']
                else:
                    logging.debug(f"Couldn't find damage for {monster.name}")
                
                drops = []
                for drop_group in monster_data['_drops']:
                    individual_drops = []
                    for drop in drop_group['drops']:
                        if 'guid' not in drop['drop']:
                            name = None
                        else:
                            name = indexer.find_name_from_guid(drop['drop']['guid'])
                        
                        individual_drops.append(
                            {
                                'item': name,
                                'chance': drop['dropChance'],
                                'amount_x': drop['dropAmount']['x'],
                                'amount_y': drop['dropAmount']['y'],
                                'percent_chance': 0
                            }
                        )
                        
                    drops.append(individual_drops)
                    
                monster.drops = drops
                monster.calculate_drop_percents()
                
                monsters.append(monster)
            except:
                pprint.pprint(components)
                logging.error(f"Could not parse {path}",exc_info=True)
                
            if report_progress is not None:
                report_progress()
        except:
            logging.error(f"Couldn't parse {path}", exc_info=True)
            
    return monsters
            

