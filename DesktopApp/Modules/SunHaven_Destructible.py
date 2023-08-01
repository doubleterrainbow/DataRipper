
import json
import logging
from DesktopApp.Modules.SunHaven_DropTable import Item
from DesktopApp.Modules.entity_with_drops import Drop, EntityWithDrops
from DesktopApp.datum import Datum

class Destructible(EntityWithDrops):
    def __init__(self):
        super().__init__()
        self.health = 0.0
        self.exp = 0.0
        self.double_scythe_damage = False
        
    def __str__(self):
        original = super().__str__()
        
        ret = original.split("\n")[0] + "\n"
        
        if self.health:
            ret += f"Health = {self.health}\n"
        
        if self.exp:
            ret += f"Exp = {self.exp}\n"
        
        if self.double_scythe_damage:
            ret += f"Double Damage from Scythe\n"
        
        return ret + "\n".join(original.split("\n")[1:])
    
        
    def calculate_drop_percents(self):
        if not self.drops:
            return
        
        percent_drops = [d.chance for d in self.drops if d.chance < 0]

        if percent_drops:
            for drop in self.drops:
                drop.percent_chance = drop.chance * 100 
        else:
            super().calculate_drop_percents()
                

def getDestructible(jsonPath):
    # Opening JSON file
    f = open(jsonPath)
    data = json.load(f)

    obj = {}
    
    if 'drops' in data:
        drops = data['drops']['drops']
        obj = Destructible()
        obj.name = ""
        
        if 'health' in data:
            obj.health = float(data['health'])
        
        if 'exp' in data:
            obj.exp = float(data['exp'])
        
        if 'doubleDamageFromScythe' in data:
            obj.double_scythe_damage = data['doubleDamageFromScythe']
        
        for i in drops:
            obj.drops.append(
                Drop(1, str(i['drop']['m_PathID']), -1, "", float(i['dropChance']), i['dropAmount'])
            )
    
        try:
            obj.calculate_drop_percents()
        except Exception as e:
            logging.error(f"Error calculating drop %s for destructible - {jsonPath}", exc_info=True)
    
    # Closing file
    f.close()

    return obj
