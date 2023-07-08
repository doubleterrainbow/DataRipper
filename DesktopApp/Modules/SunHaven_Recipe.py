# import required module
import json

class Recipe:
  def __init__(self):
    self.inputs = []
    self.output = {}
    self.craftTime = 0
    self.filename = ""

class Item:
  def __init__(self, pID, gID, name, amount):
    self.pID = pID
    self.gID = gID
    self.name = name
    self.amount = amount

def getRecipe(jsonPath):
    # Opening JSON file
    f = open(jsonPath)
    data = json.load(f)

    recipe = Recipe()
    
    # Iterating through the json list
    if data['input'] == []:
      for i in data['serializationData']['ReferencedUnityObjects']:
        recipe.inputs.append(
            Item(str(i['m_PathID']), -1, '', 'Unknown')
        )
    else:
      for i in data['input']:
        recipe.inputs.append(
            Item(str(i['item']['m_PathID']), -1, '', str(i['amount']))
        )
      
        
    recipe.output = Item(str(data['output']['item']['m_PathID']), -1, '',
             str(data['output']['amount']))

    recipe.craftTime = str(data['hoursToCraft'])

    # Closing file
    f.close()

    return recipe
