import csv
import os
import re
import json
import operator
import logging
import itertools

from DesktopApp.Modules import SunHaven_Utilities as utils
from DesktopApp.Modules import SunHaven_Cutscene as CutsceneParser
from DesktopApp.Modules import SunHaven_Dialogue as DialogueParser
from DesktopApp.Modules import SunHaven_DropTable as DropTableParser
from DesktopApp.Modules import SunHaven_Destructible as DestructibleParser
from DesktopApp.Modules import SunHaven_Seed as SeedParser
from DesktopApp.Modules import SunHaven_Animals as AnimalsParser
from DesktopApp.Modules import SunHaven_Item as ItemParser
from DesktopApp.Modules import SunHaven_FishingNet as FishingNetParser
from DesktopApp.Modules import SunHaven_FishSpawner as FishSpawnerParser
from DesktopApp.Modules import SunHaven_GiftTable as GiftTableParser
from DesktopApp.Modules import SunHaven_Merchant as MerchantParser
from DesktopApp.Modules import SunHaven_Recipe as RecipeParser
from DesktopApp.Modules import SunHaven_RecipeList as RecipeListParser
from DesktopApp.Modules import SunHaven_StattedItem as StattedItemParser
from DesktopApp.Modules import SunHaven_Tool as ToolParser
from DesktopApp.Modules import SunHaven_Quest as QuestParser
from DesktopApp.Modules import SunHaven_Book as BookParser
from DesktopApp.datum import Datum
from asset_ripper_parser.file_tags import FileTags
from DesktopApp.parser import Parser
from DesktopApp.progress import Progress
from DesktopApp.linker_registry import LinkerRegistry

def jsonParse(parser: Parser, srcPaths, getFunc):
    
    def parseFile(fullPath, filename, objList):
        logging.debug('Loading ' + filename)
        r = getFunc(fullPath)
        if r:
            r.filename = filename
            objList.append(r)

    objList = []
    if isinstance(srcPaths, str):
        srcPaths = [srcPaths]

    for srcPath in srcPaths:
        folderPath = os.path.join(parser.dataPath, srcPath)
        if os.path.isdir(folderPath):
            for filename in os.listdir(folderPath):
                f = os.path.join(folderPath, filename)
                if os.path.isfile(f):
                    parseFile(f,filename,objList)
        elif os.path.isfile(folderPath):
            parseFile(folderPath,os.path.basename(srcPath),objList)
        else:
            logging.debug('File: ' + folderPath + " cannot be found")

    return objList

@LinkerRegistry.register("Cutscenes")
def linkCutscenes(parser: Parser, srcPaths, dstPath):

    objList = jsonParse(parser, srcPaths, CutsceneParser.getCutscene)
    parser.on_progress_update(Progress( f"Found {str(len(objList))} Cutscene Options..."))
    logging.debug("Found " + str(len(objList)) + " Cutscene Options.")

    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    f = open(dstPath, "w", encoding="utf8")
    for obj in objList:
        f.write(str(obj) + '\n')
    f.close()
    
    parser.on_progress_update(Progress( f"Finished creating {str(len(objList))} Cutscenes..."))
    

@LinkerRegistry.register("Dialogues")
def linkDialogues(parser, srcPaths, dstPath):

    objList = jsonParse(parser, srcPaths, DialogueParser.getDialogue)
    logging.debug("Found " + str(len(objList)) + " Dialogue Options.")
    parser.on_progress_update(Progress( f"Found {str(len(objList))} Dialogue Options."))

    green = "#3cb043"
    red = "#dc2626"
    quest = "#710193"
    heart = '{{il|Heart|icon|size=14px}} Points'
    relationshipStr = """<span style="color: {0};">'''{1}'''</span>"""

    
    parser.on_progress_update(Progress( f"Finished adding icons in dialogues..."))

    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    f = open(dstPath, "w", encoding="utf8")
    for obj in objList:
        f.write(obj.filename + ': ' + obj.npc + ' - ' + obj.occurance + '\n')

        if obj.oneliner:
            for line in obj.oneliner:
                line = utils.wikifyColorTags(replaceNotes(line) + addIcons(obj.filename))
                f.write('|-\n|{{OneLiner|' + line + '}}\n')
                #f.write(': ' + i + '\n')
        elif obj.cycle:
            for k in obj.cycle:
                line = utils.wikifyColorTags(replaceNotes(obj.cycle[k]))
                f.write('|' + k + '=' + line +'\n')
                #f.write(': ' + k + " - " + l + '\n')
        else:
            logging.debug('Error in ' + obj.filename)

        f.write('\n')
    f.close()
    
    parser.on_progress_update(Progress( f"Finished parsing dialogues..."))

@LinkerRegistry.register("Destructibles", [FileTags.Destructible])
def linkDestructibles(parser: Parser, srcPaths, dstPath):

    objList = jsonParse(parser, srcPaths[FileTags.Destructible.value], DestructibleParser.getDestructible)
    logging.debug("Found " + str(len(objList)) + " entities with health and drops.")
    parser.on_progress_update(Progress( f"Found {str(len(objList))} entities with health and drops."))

    datumList = []
    for o in objList:
        datumList.extend([x for x in o.drops])
    datumList.extend([x.destructible for x in objList])
    parser.assets_parser.csvParseAssetFile(datumList)
    
    parser.on_progress_update(Progress( f"Writing destructibles to file..."))

    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    f = open(dstPath, "w")
    for obj in objList:
        if 'DestructibleDecoration' not in obj.filename:
            f.write(str(obj) + '\n')
    f.close()
    
    parser.on_progress_update(Progress( f"Finished parsing destructibles..."))

@LinkerRegistry.register("Seeds", [FileTags.Seed])
def linkSeeds(parser: Parser, srcPaths, dstPath):
    
    objList = jsonParse(parser, srcPaths[FileTags.Seed.value], SeedParser.getSeed)
    logging.debug("Found " + str(len(objList)) + " seeds.")
    parser.on_progress_update(Progress( f"Found {str(len(objList))} seeds."))

    parser.on_progress_update(Progress( f"Getting seed prices..."))
    all_files = parser.assets_parser.csvParseMetadataFile(parser.dstPath)
    merchant_lists = [x['filename'] for x in all_files if 'merchant table' in x['tags'] and \
        ("General" in x['filename'] or "Farming" in x['filename'] or "Seeds" in x['filename'])]
    
    merchants = jsonParse(parser, merchant_lists, MerchantParser.getMerchant)
    merchant_datums = []
    for o in merchants:
        merchant_datums.extend([x for x in o.items])
    parser.assets_parser.csvParseAssetFile(merchant_datums)
    
    merchant_items = []
    for merchant in merchants:
        for item in merchant.items:
            merchant_items.append(item)
    
    for seed in objList:
        matching_item = [item for item in merchant_items if item.name == seed.name]
        if matching_item:
            seed.buy_price = int(matching_item[0].value)
    
    parser.on_progress_update(Progress( f"Writing seeds to file..."))

    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    f = open(dstPath, "w")
    for obj in objList:
        f.write(str(obj) + '\n\n')
    f.close()
    
    with open(dstPath.replace(".txt", "_formatted.txt"), 'w') as formatted_file:
        written_seeds = []
        for obj in objList:
            if obj.name not in written_seeds:
                formatted_file.write(obj.to_wiki_tags() + '\n\n')
                written_seeds.append(obj.name)
    
    parser.on_progress_update(Progress( f"Finished parsing seeds..."))

@LinkerRegistry.register("Animals", [FileTags.Animal])
def linkAnimals(parser: Parser, srcPaths, dstPath):
    animals = jsonParse(parser, srcPaths[FileTags.Animal.value], AnimalsParser.getAnimalTable)
    logging.debug("Found " + str(len(animals)) + " animals.")
    parser.on_progress_update(Progress( f"Found {str(len(animals))} animals."))

    datumList = []
    for o in animals:
        datumList.extend([x for x in o.drops])
    datumList.extend([x.expected_drop for x in animals if x.expected_drop is not None])
    datumList.extend([x.golden_drop for x in animals if x.golden_drop is not None])
    parser.assets_parser.csvFindPossibleMatches(datumList)
    
    parser.on_progress_update(Progress( f"Writing animals to file..."))

    # remove this code block to include duplicate animals
    unique_animals = {}
    for anim in animals:
        unique_animals[anim.name] = anim

    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    f = open(dstPath, "w")
    for animal in unique_animals.values():
        f.write(str(animal) + '\n')
    f.close()
    
    parser.on_progress_update(Progress( f"Finished parsing animals..."))

@LinkerRegistry.register("Fishing Nets", [FileTags.FishNet])
def linkFishingNets(parser: Parser, srcPaths, dstPath):
    
    objList = jsonParse(parser, srcPaths[FileTags.FishNet.value], FishingNetParser.getFishingNet)
    logging.debug("Found " + str(len(objList)) + " Fishing Nets.")
    parser.on_progress_update(Progress( f"Found {str(len(objList))} Fishing nets."))
    
    datumList = []
    for o in objList:
        datumList.extend([x for x in o.drops])
    parser.assets_parser.csvParseAssetFile(datumList)
    parser.on_progress_update(Progress( f"Writing fishing nets file..."))

    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    with open(dstPath, "w") as fishing_net_file:
        for obj in objList:
            fishing_net_file.write(obj.size + ' Fishing Net:')
            for item in obj.drops:
                fishing_net_file.write("- "+item.assetType + ': ' + item.name + ' @ ' + item.chance + '%\n')
            fishing_net_file.write('\n')
    parser.on_progress_update(Progress( f"Finished writing fishing nets..."))

@LinkerRegistry.register("Fish Spawners", [FileTags.FishSpawner])
def linkFishSpawners(parser: Parser, srcPaths, dstPath):
    
    objList = jsonParse(parser, srcPaths[FileTags.FishSpawner.value], FishSpawnerParser.getFishSpawner)
    logging.debug("Found " + str(len(objList)) + " Fish Spawners.")
    
    datumList = []
    for o in objList:
        datumList.extend([x for x in o.drops])
    parser.assets_parser.csvParseAssetFile(datumList)
    parser.on_progress_update(Progress(f"Writing fish spawners to file..."))
    
    # Get somewhat usable names of fish spawners
    spawner_refs = []
    
    with open(parser.assets_parser.references_path, 'r') as ref_file:
        for line in ref_file.readlines():
            pieces = line.split(",")
            if re.match("[A-Za-z]+FishSpawner.*", pieces[2]) is not None:
                spawner_refs.append(Datum(pieces[0], pieces[1], pieces[2].replace("FishSpawner", "")))
                
    for spawner in objList:
        ref = [x for x in spawner_refs if str(x.pID) == str(spawner.location.pID)]
        if ref:
            spawner.location = ref[0]

    # Convert list into a Set containing only unique values
    objSet = []
    objSet.append(objList[0])
    for oList in objList:
        hasSame = False
        for oSet in objSet:
            # If the drops length differs, they are not the same
            if len(oList.drops) == len(oSet.drops):
                # Check each drop, if any is different, the drops are different
                for idx in range(len(oList.drops)):
                    if oList.drops[idx].name != oSet.drops[idx].name:
                        break
                    elif oList.drops[idx].chance != oSet.drops[idx].chance:
                        break
                else:
                    hasSame = True

            if hasSame:
                break
        else:
            objSet.append(oList)
    logging.debug(len(objSet))
    
    parser.on_progress_update(Progress("Calculating fish spawn percentages..."))
    
    rarities = {}
    
    logging.debug("Getting fish rarities to calculate spawn % chance")
    for spawn in objSet:
        logging.debug(f"Calculating spawner {spawn.filename}")
        
        # Find item to get rarity
        for fish in [x for x in spawn.drops if x.name]:
            if fish.name in rarities.keys():
                fish.rarity = rarities[fish.name]
                continue
            
            relevant_files = []
            with open(parser.dstPath, 'r') as file_types:
                relevant_files = [line for line in file_types.readlines() if fish.name in line and "item,craftable" in line]
            
            for file in relevant_files:
                try:
                    with open(os.path.join(parser.dataPath, file.split(',')[0].rstrip()), 'r') as data_file:
                        data = json.load(data_file)
                        if data["name"] != fish.name:
                            continue
                        else:
                            rarity = int(data["rarity"])
                            if rarity == 0:
                                fish.rarity = "Common"
                            elif rarity == 1:
                                fish.rarity = "Uncommon"
                            elif rarity == 2:
                                fish.rarity = "Rare"
                            elif rarity == 3:
                                fish.rarity = "Epic"
                            elif rarity == 4:
                                fish.rarity = "Legendary"
                            
                            rarities[fish.name] = fish.rarity
                            break
                        
                except FileNotFoundError:
                    logging.warning(f"Couldn't find file {file} while looking for {fish.name}")
            
            
        spawn.calculate_percent_chance()

    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    f = open(dstPath, "w")
    
    for obj in objSet:
        f.write(f"{obj}\n\n")
        
    f.close()
    parser.on_progress_update(Progress(f"Sorting and writing to another file..."))
    
    sorted_fish = []
    for spawner in objSet:
        for fish_spawn in spawner.drops:
            sorted_fish.append({
                "location": re.sub(r"\([0-9]+\)", "", spawner.location.name.rstrip()).rstrip(), 
                "fish_name": fish_spawn.name, 
                "fish": fish_spawn
            })
            
    sorted_fish.sort(key=lambda x: x["fish_name"])
    
    with open(f"{dstPath.split('.txt')[0]}_SortedByFish.txt", "w") as sorted_file:
        fish_name = None
        location_name = None
        region = None
        writing = []
        for fish in sorted_fish:
            if fish_name != fish['fish_name']:
                writing.append("\n{{Fishing spawn/footer")
                writing.append(f"|note = ")
                writing.append("}}")
                
                sorted_file.write('\n'.join(writing))
                sorted_file.write("\n--------------------------------\n")
                writing = []
                
                writing.append("{{Fishing spawn/header")
                writing.append(f"|name = {fish['fish_name']}")
                writing.append("}}\n")
                location_name = None
                region = None
                fish_name = fish['fish_name']
                
            if location_name != fish['location']:
                location_name = fish['location']
                
                if "Withergate" in location_name:
                    region = "Withergate"
                elif "Nelvari" in location_name:
                    region = "Nelvari"
                else:
                    region = "Sun Haven"
                    
                location_name = location_name.replace(region, "")
                
                if location_name == "Beach":
                    location_name = "Sea"
                elif location_name == "PlayerFarm":
                    location_name = "Farm"
                
            spawn = ["{{Fishing spawn"]
            spawn.append(f"|{fish['fish'].season}")
            spawn.append(f"|{location_name}")
            spawn.append(f"|{round(fish['fish'].min_percent_chance, 2)}%")
            spawn.append(f"|{round(fish['fish'].max_percent_chance, 2)}%")
            spawn.append("}}")
            writing.append("".join(spawn))
            
            if location_name == 'Farm':
                spawn = ["{{Fishing spawn"]
                spawn.append(f"|{fish['fish'].season}")
                spawn.append(f"|Town")
                spawn.append(f"|{round(fish['fish'].min_percent_chance, 2)}%")
                spawn.append(f"|{round(fish['fish'].max_percent_chance, 2)}%")
                spawn.append("}}")
                writing.append("".join(spawn))
            elif location_name == 'Town':
                spawn = ["{{Fishing spawn"]
                spawn.append(f"|{fish['fish'].season}")
                spawn.append(f"|Farm")
                spawn.append(f"|{round(fish['fish'].min_percent_chance, 2)}%")
                spawn.append(f"|{round(fish['fish'].max_percent_chance, 2)}%")
                spawn.append("}}")
                writing.append("".join(spawn))
            
    parser.on_progress_update(Progress(f"Finished writing fish spawners to file..."))    

@LinkerRegistry.register("Statted Items", [FileTags.STATTED])
def linkStattedItems(parser, srcPaths, dstPath):
    objList = jsonParse(parser, srcPaths[FileTags.STATTED.value], StattedItemParser.getStattedItem)
    logging.debug(f"Found {str(len(objList))} Statted Items.")
    parser.on_progress_update(Progress( f"Found {str(len(objList))} Statted Items."))
    
    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    f = open(dstPath, "w")
    for obj in objList:
        f.write(obj.filename + '\n')
        f.write(': ' + obj.description + '\n')
        f.write(': Details\n')
        f.write('- Type: ' + obj.armorType + '\n')
        f.write('- Set: ' + obj.armorSet + '\n')
        f.write('- Material:' + obj.armorMaterial + '\n')
        f.write('- Req. Level' + obj.requiredLevel + '\n')
        f.write(': Stats\n')
        for item in obj.stats:
            f.write("- "+item.type + " @ " + item.value + '\n')
        f.write('\n')
    f.close()
    parser.on_progress_update(Progress( f"Finished writing statted items..."))

@LinkerRegistry.register("Tools")
def linkTools(parser: Parser, srcPaths, dstPath):
    objList = jsonParse(parser, srcPaths, ToolParser.getTool)
    logging.debug(f"Found {str(len(objList))} Tools.")
    parser.on_progress_update(Progress( f"Found {str(len(objList))} Tools."))
    
    datumList = [x for x in objList]
    parser.assets_parser.csvParseAssetFile(datumList)
    parser.on_progress_update(Progress( f"Writing tools file..."))
    

    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    f = open(dstPath, "w")
    for obj in objList:
        f.write(obj.filename + ' - ' + obj.name + '\n')
        f.write(': ' + obj.description + '\n')
        f.write(': Details\n')
        f.write('- Type: ' + str(obj.weaponType) + '\n')
        f.write('- Metal: ' + str(obj.isMetalTool) + '\n')
    f.close()
    
    parser.on_progress_update(Progress( f"Finished writing tools file..."))

@LinkerRegistry.register("Books", [FileTags.Readable])
def linkBooks(parser: Parser, srcPaths, dstPath):
    books = jsonParse(parser, srcPaths[FileTags.Readable.value], BookParser.getBook)
    logging.debug(f"Found {str(len(books))} Books.")
    parser.on_progress_update(Progress( f"Found {str(len(books))} Books."))
    
    # datumList = [x for x in books]
    # parser.assets_parser.csvParseAssetFile(datumList)
    parser.on_progress_update(Progress( f"Writing books file..."))
    
    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    f = open(dstPath, "w")
    for book in books:
        f.write(f"{book.book_name}\n")
        f.write(f"{book.text}\n\n")
    f.close()
    
    parser.on_progress_update(Progress( f"Finished writing books file..."))
    
@LinkerRegistry.register("Quests", [FileTags.QUEST])
def linkQuests(parser: Parser, srcPaths, dstPath):

    objList = jsonParse(parser, srcPaths[FileTags.QUEST.value], QuestParser.getQuest)
    logging.debug(f"Found {str(len(objList))} Quests.")
    parser.on_progress_update(Progress( f"Found {str(len(objList))} Quests."))
    
    datumList = []
    for o in objList:
        datumList.extend([x for x in o.inputs])
        datumList.extend([x for x in o.rewards])
        datumList.extend([x for x in o.choiceRewards])
        datumList.extend([x for x in o.characterProgressRequirements])
        datumList.extend([x for x in o.worldProgressRequirements])
    parser.assets_parser.csvParseAssetFile(datumList)
    parser.on_progress_update(Progress( f"Writing quests file..."))
    
    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    f = open(dstPath, "w")
    for obj in objList:
        f.write(str(obj) + '\n')
    f.close()
    parser.on_progress_update(Progress( f"Finished writing quests file..."))

def start_linking(parser: Parser, enabled_linkers):
    linkers = LinkerRegistry.linkers
    all_files = parser.assets_parser.csvParseMetadataFile(parser.dstPath)
    
    progress = 0
    
    for linker in linkers:
        files = []
        
        if linker.label in enabled_linkers:
            # TODO: there's gotta be a better way
            if linker.tags is None:
                if linker.label == "Cutscenes": 
                    files = [os.path.join(parser.codePath,x) for x in os.listdir(parser.codePath) if ('Cutscene' in x)]
                elif linker.label == "Dialogues":
                    files = 'TextAsset'
            else:
                files = {}
                for tag in linker.tags:
                    files[tag.value] = [x['filename'] for x in all_files if (tag.value in x['tags'])]
            try:
                linker.callable(parser, files, os.path.join(parser.outputPath, parser.gameVersion, linker.output_filename))
                progress += 1
                parser.on_progress_update(Progress(f"Finished linking {linker.label}", current_progress=progress, max_progress=len(enabled_linkers)))
            except Exception as e:
                parser.on_progress_update(Progress(f"Error when linking {linker.label}", error=e))
                logging.error(f"Error when linking {linker.label}", exc_info=True)
            

    parser.on_progress_update(Progress(f"Finished!", complete=True))
    logging.debug('Done!')
