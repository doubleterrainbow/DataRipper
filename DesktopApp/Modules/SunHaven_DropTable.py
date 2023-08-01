# import required module
import json
import logging
from DesktopApp.Modules.SunHaven_Animals import Animal
from DesktopApp.Modules.entity_with_drops import Drop, EntityWithDrops

from DesktopApp.datum import Datum

class Enemy(EntityWithDrops):
    def __init__(self):
        super().__init__()
        self.health = ""
        self.experience = ""
        self.level = ""
        self.spawner = ""
        self.defense = ""
        self.flying = ""
        self.ranged = False

    def __str__(self):
        original = super().__str__()
        
        ret = original.split("\n")[0] + f" ({self.spawner})"
        ret += "\n:Details\n"
        ret += "- Level: " + str(self.level) + '\n'
        ret += "- Health: " + str(self.health) + '\n'
        ret += "- Exp: " + str(self.experience) + '\n'
        ret += "- Defense: " + str(self.defense) + '\n'
        ret += "- Flying: " + str(self.flying) + '\n'
        ret += "- Ranged: " + str(self.flying) + '\n'
        
        ret += "\n".join([line for line in original.split("\n")[1:] if "Nothing" not in line])
        
        return ret
    
    def __eq__(self, __value: object) -> bool:
        return self.name == __value.name and self.level == __value.level and self.spawner == __value.spawner

class Item(EntityWithDrops):
    def __init__(self):
        super().__init__()

def getDropTable(jsonPath):
    # Opening JSON file
    f = open(jsonPath)
    data = json.load(f)

    obj = {}
    
    if '_foliage' in data:
        drops = data['_foliage']['drops']
        obj = Item()
        obj.name = ""
        
        for i in drops:
            obj.drops.append(
                Drop(1, str(i['drop']['m_PathID']), -1, "", float(i['dropChance']), i['dropAmount'])
            )
    
        try:
            obj.calculate_drop_percents()
        except Exception as e:
            logging.error(f"Error calculating drop %s for foliage in {jsonPath}", exc_info=True)
    
    # Iterating through the json list
    if '_drops' in data:
        if data['_drops']:
            if 'enemyName' in data:
                obj = Enemy()
                obj.name = data['enemyName']
                obj.spawner = data['enemySpawnerName']
                obj.health = str(data['_health'])
                obj.experience = str(data['_experience'])
                obj.level = str(data['_powerLevel'])
                obj.defense = str(data['defense'])
                obj.flying = str(data['flying'])
                obj.ranged = "Monkey" in jsonPath
            elif 'animalName' in data:
                obj = Animal()
                obj.name = data['animalName']
            elif obj == {}:
                obj = Item()
                obj.name = ""

            drop_index = 0
            
            for d in data['_drops']:
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
