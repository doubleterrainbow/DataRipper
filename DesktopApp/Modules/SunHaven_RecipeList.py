# import required module
import json

class RecipeList:
  def __init__(self):
    self.items = []
    self.filename = ""

class Craftable:
  def __init__(self, pID, gID, name):
    self.pID = pID
    self.gID = gID
    self.name = name

def getRecipeList(jsonPath):
    # Opening JSON file
    f = open(jsonPath)
    data = json.load(f)

    obj = RecipeList()
    
    # Iterating through the json list
    for i in data['craftingRecipes']:
        obj.items.append(
            Craftable(str(i['m_PathID']), -1, '')
        )

    # Closing file
    f.close()

    return obj
