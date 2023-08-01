
import logging
from typing import List

from DesktopApp.datum import Datum

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
            
        return f"{amount_str} {self.name} => {round(self.percent_chance, 2)}% (weight = {self.chance})\n"


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
    
    def __eq__(self, __value: object) -> bool:
        return self.name == __value.name

    def calculate_drop_percents(self):
        if not self.drops:
            return

        max_drop_index = max([drop.dropGroupIndex for drop in self.drops])        
        for i in range(1, max_drop_index + 1):
            group = [drop for drop in self.drops if drop.dropGroupIndex == i]
            total_weight = sum([drop.chance for drop in group])
            
            for drop in group:
                drop.percent_chance = (drop.chance / total_weight) * 100 
                
    def to_wiki_format(self) -> str:
        result = []
        result.append("{{" + f"Item drop/header|name={self.name}" + "}}")
        
        for drop in self.drops:
            x = 0
            y = 0
            if 'm_Y' in drop.amount:
                x = drop.amount['m_X']
                y = drop.amount['m_Y']
            elif 'y' in drop.amount:
                x = drop.amount['y']
                y = drop.amount['x']
            else:
                logging.debug('Amount unknown: ' + drop.amount)

            amount_str = str(x)
            if x != y:
                amount_str = f"{x}-{y}"

            if y != 0:
                result.append("{{" + f"Item drop|{drop.name}|{amount_str}|{round(drop.percent_chance, 2)}%" + "}}")
            
        result.append("{{Item drop/footer}}")
        
        return "\n".join(result)
                
