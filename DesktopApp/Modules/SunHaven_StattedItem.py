# import required module
import json

class StattedItem:
  def __init__(self):
    self.stats = []
    self.filename = ""
    self.description = ""

    self.armorType = ""
    self.armorSet = ""
    self.armorMaterial = ""
    self.requiredLevel = ""

class Stat:
  def __init__(self, statType, value):
    self.type = statType
    self.value = value

statTypes = ["Health","Mana","AttackDamage","AttackSpeed","HealthRegen","ManaRegen","Movespeed","Jump","SpellDamage","MeleeLifesteal","RangedLifeSteal","MovespeedOnHit","MovespeedOnKill","HealthOnKill","Crit","DamageReduction","GoldGain","Knockback","StunDuration","Size","FishingSkill","MiningSkill","ExplorationSkill","Defense","FlatDamage","RomanceBonus","MoneyPerDay","BonusCombatEXP","BonusWoodcuttingEXP","BonusFishingEXP","BonusMiningEXP","BonusCraftingEXP","BonusFarmingEXP","StunChance","Accuracy","FarmingSkill","GoldPerCraft","MiningCrit","WoodcuttingCrit","SmithingSkill","BonusExperience","SpellPower","SwordPower","CrossbowPower","CritDamage","Dodge","FreeAirSkipChance","FishingMinigameSpeed","FishBobberAttraction","EnemyGoldDrop","ExtraForageableChance","BonusTreeDamage","MiningDamage","FallDamageReduction","MovementSpeedAfterRock","FruitManaRestore","SpellAttackSpeed","Power","WoodcuttingDamage","CommunityTokenPerDay","TicketsPerDay","TripleGoldChance","PickupRange","ExtraCropChance","FishingWinArea","FishingSweetSpotArea","ManaPerCraft","BlackGemDropChance","CraftingSpeed"]
armorMaterials = ["None", "Metal", "MageRobes", "Archer"]
armorSets = ["None", "Copper", "Iron", "Adamant", "Mithril", "Sunite", "Withergate", "Mage", "Archer", "Legionnaire", "Anubis"]
armorTypes = ["Chest", "Pants", "Gloves", "Hat", "Back", "Ring", "Amulet", "Keepsake"]

def getStattedItem(jsonPath):
    # Opening JSON file
    f = open(jsonPath)
    data = json.load(f)

    obj = {}
    
    # Iterating through the json list
    if 'stats' in data:
        obj = StattedItem()
        obj.filename = data['m_Name']
        obj.description = data['description']
        obj.armorType = armorTypes[data['armorType']]
        obj.armorSet = armorSets[data['armorSet']]
        obj.armorMaterial = armorMaterials[data['armorMaterial']]
        obj.requiredLevel = str(data['requiredLevel'])
        for i in data['stats']:
            obj.stats.append(
                Stat(statTypes[i['statType']], str(i['value']))
            )


    # Closing file
    f.close()

    return obj
