# import required module
import json
import logging
from typing import List

from DesktopApp.datum import Datum

class EntityWithDrops:
    def __init__(self):
        self.drops: List[Drop] = []
        self.filename = ""
        self.name = ""
        
    
    def __str__(self):
        ret = str(self.filename) + ": " + str(self.name) + '\n'
        ret += ':Drops\n'
        for item in self.drops:
            ret += f"- {item}"
        
        return ret

    def calculate_drop_percents(self):
        if not self.drops:
            return

        max_drop_index = max([drop.dropGroupIndex for drop in self.drops])        
        for i in range(1, max_drop_index + 1):
            group = [drop for drop in self.drops if drop.dropGroupIndex == i]
            total_weight = sum([drop.chance for drop in group])
            
            for drop in group:
                drop.percent_chance = (drop.chance / total_weight) * 100 
                

class Enemy(EntityWithDrops):
    def __init__(self):
        super().__init__()
        self.health = ""
        self.experience = ""
        self.level = ""
        self.spawner = ""

    def __str__(self):
        original = super().__str__()
        
        ret = original.split("\n")[0]
        ret += "\n:Details\n"
        ret += "- Level: " + str(self.level) + '\n'
        ret += "- Health: " + str(self.health) + '\n'
        ret += "- Exp: " + str(self.experience) + '\n'
        
        ret += "\n".join([line for line in original.split("\n")[1:] if "Nothing" not in line])
        
        return ret

class Item(EntityWithDrops):
    def __init__(self):
        super().__init__()

class Drop(Datum):
    def __init__(self, dropGroupIndex, pID, gID, name, chance, amount):
        super().__init__(pID, gID, name)
        self.dropGroupIndex = dropGroupIndex
        self.chance = chance
        self.amount = amount
        self.percent_chance = 0.0
        self.item_candidates = []
        
    def __str__(self):
        x = 0
        y = 0
        if 'm_Y' in self.amount:
            x = self.amount['m_X']
            y = self.amount['m_Y']
        elif 'y' in self.amount:
            x = self.amount['y']
            y = self.amount['x']
        else:
            logging.debug('Amount unknown: ' + self.amount)

        if y == 0:
            self.name = "Nothing"
        
        amount_str = str(x)
        if x != y:
            amount_str = f"{x}-{y}"
            
        return f"{amount_str} {self.name:<30} @ {self.chance:<5} => {round(self.percent_chance, 2)}%\n"

def getDropTable(jsonPath):
    # Opening JSON file
    f = open(jsonPath)
    data = json.load(f)

    obj = {}
    
    # Iterating through the json list
    if ('_drops' in data):
        if (len(data['_drops']) > 0):
            if 'enemyName' in data:
                obj = Enemy()
                obj.name = data['enemyName']
                obj.spawner = data['enemySpawnerName']
                obj.health = str(data['_health'])
                obj.experience = str(data['_experience'])
                obj.level = str(data['_powerLevel'])
            elif obj == {}:
                obj = Item()
                obj.name = ""

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
                logging.error(f"Error calculating drop %s for {obj.name} in {jsonPath}", exc_info=True)

    # Closing file
    f.close()

    return obj
