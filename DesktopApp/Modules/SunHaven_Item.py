# import required module
import json
import os

class Item:
    def __init__(self):
        self.filename = ""
        self.name = ""
        self.pID = ""
        self._gID = ""
        self.description = ""

        self.stackSize = ""
        self.coinSell = ""
        self.ticketSell = ""
        self.orbSell = ""
        self.rarity = ""
        self.hearts = ""

    def __str__(self):
        ret = str(self.filename) + ": " + str(self.gID) + " - " + str(self.name) + '\n'
        ret += ":" + str(self.description) + '\n'
        ret += "- Rarity: " + str(self.rarity) + '\n'
        ret += "- Hearts: " + str(self.hearts) + '\n'
        ret += "- Stack: " + str(self.stackSize) + '\n'
        ret += ":Sell\n"
        ret += "- Coins: " + str(self.coinSell) + '\n'
        ret += "- Orbs: " + str(self.orbSell) + '\n'
        ret += "- Tickets: " + str(self.ticketSell) + '\n'

        return ret

    @property
    def gID(self):
        return int(self._gID)

    @gID.setter
    def gID(self, value):
        self._gID = value

class Food(Item):
    def __init__(self):
        super().__init__()
        self.foodStat = {}
        self.health = ""
        self.mana = ""
        self.exps = []
        self.maxStats = []
        self.statBuffs = []

    def __str__(self):
        ret = super().__str__()

        ret += ":Details\n"
        ret += "- Health: " + str(self.health) + '\n'
        ret += "- Mana: " + str(self.mana) + '\n'
        ret += "- Perm Bonus: "+ str(self.foodStat) + '\n'
        
        ret += ':EXP\n'
        for stat in self.exps:
            ret += "- " + str(stat) + '\n'

        ret += ':Max Stats\n'
        for stat in self.maxStats:
            ret += "- " + str(stat) + '\n'
            
        ret += ':Stat Buffs\n'
        for stat in self.statBuffs:
            ret += "- " + str(stat) + '\n'

        return ret

class Armor(Item):
    def __init__(self):
        super().__init__()
        self.stats = []
        self.armorType = ""
        self.armorSet = ""
        self.armorMaterial = ""
        self.requiredLevel = ""

    def __str__(self):
        ret = super().__str__()

        ret += ":Details\n"
        ret += "- Type: " + str(self.armorType) + '\n'
        ret += "- Set: " + str(self.armorSet) + '\n'
        ret += "- Material: "+ str(self.armorMaterial) + '\n'
        ret += "- Req Level: "+ str(self.requiredLevel) + '\n'
        
        ret += ':Stats\n'
        for stat in self.stats:
            ret += "- " + str(stat) + '\n'

        return ret

class Stat:
    def __init__(self, statType, value):
        self.type = statType
        self.value = value

    def __str__(self):
        return str(self.type) + " @ " + str(self.value)

def getItem(jsonPath):
    # Opening JSON file
    f = open(jsonPath)
    data = json.load(f)

    obj = {}
    if 'armorType' in data:
        obj = Armor()
    elif 'foodStat' in data:
        obj = Food()
    else:
        obj = Item()

    n = data['m_Name'].split(' - ')
    if len(n) > 1:
        obj.name = n[1]
        obj.gID = n[0]

    obj.description = data['description']
    obj.stackSize = data['stackSize']
    obj.coinSell = data['sellPrice']
    obj.orbSell = data['orbsSellPrice']
    obj.ticketSell = data['ticketSellPrice']
    obj.rarity = data['rarity']
    obj.hearts = data['hearts']

    statTypes = ["Health","Mana","AttackDamage","AttackSpeed","HealthRegen","ManaRegen","Movespeed","Jump","SpellDamage","MeleeLifesteal","RangedLifeSteal","MovespeedOnHit","MovespeedOnKill","HealthOnKill","Crit","DamageReduction","GoldGain","Knockback","StunDuration","Size","FishingSkill","MiningSkill","ExplorationSkill","Defense","FlatDamage","RomanceBonus","MoneyPerDay","BonusCombatEXP","BonusWoodcuttingEXP","BonusFishingEXP","BonusMiningEXP","BonusCraftingEXP","BonusFarmingEXP","StunChance","Accuracy","FarmingSkill","GoldPerCraft","MiningCrit","WoodcuttingCrit","SmithingSkill","BonusExperience","SpellPower","SwordPower","CrossbowPower","CritDamage","Dodge","FreeAirSkipChance","FishingMinigameSpeed","FishBobberAttraction","EnemyGoldDrop","ExtraForageableChance","BonusTreeDamage","MiningDamage","FallDamageReduction","MovementSpeedAfterRock","FruitManaRestore","SpellAttackSpeed","Power","WoodcuttingDamage","CommunityTokenPerDay","TicketsPerDay","TripleGoldChance","PickupRange","ExtraCropChance","FishingWinArea","FishingSweetSpotArea","ManaPerCraft","BlackGemDropChance","CraftingSpeed","MiningDamageWithergate","OrbsPerDay"]
    professionTypes = ["Combat", "Farming", "Fishing", "Mining", "Exploration"]
    increaseTypes = ["VerySmall", "Small", "Moderate", "Large", "Huge"]

    # ARMOR
    if 'armorType' in data:
        armorMaterials = ["None", "Metal", "MageRobes", "Archer"]
        armorSets = ["None", "Copper", "Iron", "Adamant", "Mithril", "Sunite", "Withergate", "Mage", "Archer", "Legionnaire", "Anubis"]
        armorTypes = ["Chest", "Pants", "Gloves", "Hat", "Back", "Ring", "Amulet", "Keepsake"]

        obj.armorType = armorTypes[data['armorType']]
        obj.armorSet = armorSets[data['armorSet']]
        obj.armorMaterial = armorMaterials[data['armorMaterial']]
        obj.requiredLevel = data['requiredLevel']
        for i in data['stats']:
            obj.stats.append(
                Stat(statTypes[i['statType']], i['value'])
            )
    
    # FOOD
    if 'foodStat' in data:
        obj.health = data['health']
        obj.mana = data['mana']
        if data['foodStat']['increase'] != 999:
            obj.foodStat = Stat(statTypes[data['foodStat']['stat']], increaseTypes[data['foodStat']['increase']])

        if len(data['statBuff']['stats']) > 0:
            for i in data['statBuff']['stats']:
                obj.statBuffs.append(
                    Stat(statTypes[i['statType']], i['value'])
                )
        for i in data['exps']:
            obj.exps.append(
                Stat(professionTypes[i['profession']], i['amount'])
            )
        for i in data['maxStats']:
            obj.maxStats.append(
                Stat(statTypes[i['statType']], i['value'])
            )

    # Closing file
    f.close()

    return obj
