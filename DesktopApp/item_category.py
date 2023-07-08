from enum import Enum

class ItemCategory(Enum):
    Equip = "equip"
    Use = "use"
    Craftable = "craftable"
    MonsterDrop = "monster drop"
    Furniture = "furniture"
    Quest = "quest item"
    
    @classmethod
    def get_index(cls, type):
        return list(cls).index(type)
    
    @classmethod 
    def from_index(cls, index):
        return list(cls)[index]
