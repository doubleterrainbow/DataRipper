# import required module
import json
import logging
from typing import List

from DesktopApp.Modules.entity_with_drops import Drop, EntityWithDrops
    
class Animal(EntityWithDrops):
    def __init__(self):
        super().__init__()
        self.expected_drop = None
        self.golden_drop = None
    
    def __str__(self):
        original = super().__str__()
        
        ret = original.split("\n")[0] + "\n"
        
        if self.expected_drop is not None or self.golden_drop is not None:
            ret += ":Expected Drops\n"
        
        if self.expected_drop is not None:
            ret += f"- Normal: {self.expected_drop.amount} {'||'.join([x.name for x in self.expected_drop.item_candidates])}\n"
        
        if self.golden_drop is not None:
            ret += f"- Golden: {self.golden_drop.amount} {'||'.join([x.name for x in self.golden_drop.item_candidates])}\n"
        
        for drop in self.drops:
            x = 0
            y = 0
            if 'm_Y' in drop.amount:
                x = drop.amount['m_X']
                y = drop.amount['m_Y']
            elif 'y' in drop.amount:
                x = drop.amount['y']
                y = drop.amount['x']

            amount_str = str(x)
            if x != y:
                amount_str = f"{x}-{y}"
            
            ret += f"{amount_str} {'||'.join([x.name for x in drop.item_candidates])} @ {drop.chance:<5} => {round(drop.percent_chance, 2)}%\n"
        
        return ret
    

def getAnimalTable(jsonPath):
    # Opening JSON file
    f = open(jsonPath)
    data = json.load(f)

    obj = Animal()
    obj.name = data['animalName']
    
    if data['itemToDrop']['m_PathID'] != 0:
        logging.debug(f"Found expected drop {data['itemToDrop']['m_PathID']} for {obj.name}")
        obj.expected_drop = Drop(0, str(data['itemToDrop']['m_PathID']), -1, "", 1.0, data['amountToDrop'])
        
    if data['goldenDrop']['m_PathID'] != 0:
        logging.debug(f"Found golden drop {data['goldenDrop']['m_PathID']} for {obj.name}")
        obj.golden_drop = Drop(0, str(data['goldenDrop']['m_PathID']), -1, "", 1.0, 1)
    
    # Iterating through the json list
    if ('_drops' in data):
        if (len(data['_drops']) > 0):
            drop_index = 0
            for d in (data['_drops']):
                drop_index += 1
                
                for i in (d['drops']):
                    obj.drops.append(
                        Drop(drop_index, str(i['drop']['m_PathID']), -1, "", float(i['dropChance']), i['dropAmount'])
                    )
            
            try:
                obj.calculate_drop_percents()
            except Exception as e:
                logging.error(f"Error calculating animal drop %s for {obj.name}", exc_info=True)

    # Closing file
    f.close()

    return obj
