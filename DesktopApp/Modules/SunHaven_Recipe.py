# import required module
import json
import re

from DesktopApp.datum import Datum

class Recipe:
  def __init__(self):
    self.inputs = []
    self.output = {}
    self.craftTime = 0
    self.filename = ""
    self.name = ""
    self.workbench = None
    self.required_progress = []
    
  def camel_case_split(self, identifier):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z0-9])|(?<=[A-Z0-9])(?=[A-Z0-9][a-z])|$)+', identifier)
    return [m.group(0) for m in matches]
  
  def to_csv(self) -> str:
      return f"{self.output.name},{self.craftTime},{self.output.sell_price},{self.output.sell_type},{';'.join([item.name + '*' + item.amount for item in self.inputs])}"
    
  def to_wiki_format(self) -> str:
    result = []
    
    result.append(f"\n\n{self.filename}")
    
    result.append("{{Recipe")
    
    workbench_label = "|workbench"
    if self.workbench is None:
        workbench_name = ""
    else:
        workbench_name = ' '.join(self.camel_case_split(self.workbench)) if ' ' not in self.workbench.rstrip() else self.workbench
    result.append(f"{workbench_label:<15} = {workbench_name}")
    
    ingredients_label = "|ingredients"
    result.append(f"{ingredients_label:<15} = {';'.join([item.name + '*' + item.amount for item in self.inputs])}")
    
    time_label = "|time"
    result.append(f"{time_label:<15} = {self.craftTime}")
    
    yield_label = "|yield"
    yield_result = str(self.output.amount) if float(self.output.amount) > 1 else "" 
    result.append(f"{yield_label:<15} = {yield_result}")
    
    recipesource_label = "|recipesource"
    recipesources = []
    for source in self.required_progress:
        pieces = self.camel_case_split(source.name)
        if source == "":
            continue
          
        recipesources.append(' '.join(pieces))
    result.append(f"{recipesource_label:<15} = {';'.join(recipesources)}")
    
    result.append("}}")
    
    return "\n".join(result)

class Item:
  def __init__(self, pID, gID, name, amount):
    self.pID = pID
    self.gID = gID
    self.name = name
    self.amount = amount
    self.sell_price = 0.0
    self.sell_type = "Coins"

def getRecipe(jsonPath):
    # Opening JSON file
    f = open(jsonPath)
    data = json.load(f)

    recipe = Recipe()
    recipe.filename = f.name

    recipe_name = data['m_Name']
    recipe_name = re.sub(r'Recipe [0-9]+ - ', '', recipe_name)
    recipe_name = re.sub(r'Recipe - ', '', recipe_name)
    recipe_name = re.sub(r'(#[0-9]+)*\.json', '', recipe_name)
    
    recipe.name = recipe_name.rstrip()
    
    # Iterating through the json list
    if data['input'] == []:
      for i in data['serializationData']['ReferencedUnityObjects']:
        recipe.inputs.append(
            Item(str(i['m_PathID']), -1, '', 'x')
        )
    else:
      for i in data['input']:
        recipe.inputs.append(
            Item(str(i['item']['m_PathID']), -1, '', str(i['amount']))
        )
      
        
    recipe.output = Item(str(data['output']['item']['m_PathID']), -1, '',
            str(data['output']['amount']))

    recipe.craftTime = str(data['hoursToCraft'])
    
    requires = []
    for progress in data['characterProgressTokens']:
        requires.append(str(progress['m_PathID']))
  
    for progress in data['worldProgressTokens']:
        requires.append(str(progress['m_PathID']))
  
    for progress in data['questProgressTokens']:
        requires.append(str(progress['m_PathID']))
        
    for x in set(requires):
        recipe.required_progress.append(Datum(x, -1, ""))
        
    # Closing file
    f.close()

    return recipe
