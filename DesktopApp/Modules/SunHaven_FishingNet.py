# import required module
import json
import xml.etree.ElementTree as ET

class FishingNet:
  def __init__(self, size, drops):
    self.size = size
    self.drops = drops
    
class Netable:
  def __init__(self, pID, gID, name, assetType, chance):
    self.pID = pID
    self.gID = gID
    self.name = name
    self.assetType = assetType
    self.chance = chance

def getFishingNet(jsonPath):
    # Opening JSON file
    f = open(jsonPath)
    data = json.load(f)

    net = FishingNet('Large' if data['large'] else 'Small', [])
    
    # Iterating through the json list
    for i in data['fish']['drops']:
        net.drops.append(Netable(str(i['drop']['m_PathID']), -1, '', 'Fish', str(i['dropChance'])))
    for i in data['oceanFish']['drops']:
        net.drops.append(Netable(str(i['drop']['m_PathID']), -1, '', 'Ocean Fish', str(i['dropChance'])))
    for i in data['craftableItems']['drops']:
        net.drops.append(Netable(str(i['drop']['m_PathID']), -1, '', 'Craftables', str(i['dropChance'])))
    for i in data['smallFish']['drops']:
        net.drops.append(Netable(str(i['drop']['m_PathID']), -1, '', 'Small Fish', str(i['dropChance'])))
    # Closing file
    f.close()

    return net
