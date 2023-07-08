# import required module
import json

class Tool:
  def __init__(self):
    self.pID = ""
    self.gID = ""
    self.filename = ""
    self.name = ""
    self.description = ""

    # Tools
    self.isMetalTool = ""
    self.weaponType = ""

    # Axe
    self.power = ""
    self.breakingPower = ""
    self.woodcuttingSkill = ""
    self.axeType = ""

    # Crossbow
    self.arrowSpeed = ""
    self.damage = ""
    self.timeBetweenArrows = ""
    self.bonusArrows = ""

    # Pickaxe
    self.power = ""
    self.breakingPower = ""
    self.pickaxeType = ""
    self.miningSkill = ""

    # Sword
    #None?

    # Hoe
    #None?

    # Fishing Rod    
    self.fishingPower = ""
    self.fishAttractionRate = ""
    self.throwDistance = ""
    self.powerIncreaseSpeed = ""
    self.fishingRodType = ""


def getTool(jsonPath):
    # Opening JSON file
    f = open(jsonPath)
    data = json.load(f)

    obj = Tool()
    
    # Iterating through the json list
    obj.pID = str(data['m_GameObject']['m_PathID'])
    obj.isMetalTool = data['_weaponType']
    obj.weaponType = data['_isMetalTool']


    # Closing file
    f.close()

    return obj
