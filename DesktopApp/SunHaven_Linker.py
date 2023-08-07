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
from DesktopApp.file_tags import FileTags
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

    def replaceNotes(line):
        note = ''
        if '//Relationship' in line:
            rString = line[line.index('//Relationship'):]
            line = line[:-len(rString)].rstrip()
            rTokens = rString.split(' ')
            for v in rTokens:
                try:
                    note = ' '+relationshipStr.format(green if int(v) > 0 else red, ('+' if int(v) > 0 else '')+v+' '+heart)
                    break
                except ValueError:
                    continue
        elif '//Emote' in line:
            rString = line[line.index('//Emote'):]
            line = line[:-len(rString)].rstrip()
        elif '//AddItem' in line:
            rString = line[line.index('//AddItem'):]
            line = line[:-len(rString)].rstrip()
            rTokens = rString.split(' ')
            note = ' '+relationshipStr.format(red, '+ {{il|'+rTokens[2]+'}}')
        elif '//Quest' in line:
            rString = line[line.index('//Quest'):]
            line = line[:-len(rString)].rstrip()
            rTokens = rString.split(' ')
            note = ' '+relationshipStr.format(quest, 'Quest: [['+rTokens[2]+']]')
        elif '//Charon' in line:
            line = line[:line.index('//Charon')].rstrip()
        return (line + note).strip()

    parser.on_progress_update(Progress( f"Finished replacing wierd text in dialogues..."))

    def addIcons(filename):
        season = None
        if 'Spring' in filename:
            season = 'icon_spring'
        elif 'Summer' in filename:
            season = 'icon_summer'
        elif 'Fall' in filename:
            season = 'icon_fall'
        elif 'Winter' in filename:
            season = 'icon_winter'

        relationship = None
        if 'Dating' in filename:
            relationship = 'Love Letter'
        elif 'Married' in filename:
            relationship = 'Wedding Ring'
        
        icons = ''
        if relationship:
            icons = ' {{{{il|{0}|icon}}}}'.format(relationship)
        if season:
            icons += ' {{{{il|{0}|icon}}}}'.format(season)
        
        return icons

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

@LinkerRegistry.register("Drop Tables", [FileTags.DropTable])
def linkDropTables(parser: Parser, srcPaths, dstPath):

    objList = jsonParse(parser, srcPaths[FileTags.DropTable.value], DropTableParser.getDropTable)
    logging.debug("Found " + str(len(objList)) + " enemies with drop tables.")
    parser.on_progress_update(Progress( f"Found {str(len(objList))} enemies with drop tables."))

    datumList = []
    for o in objList:
        datumList.extend([x for x in o.drops])
    parser.assets_parser.csvParseAssetFile(datumList)
    
    parser.on_progress_update(Progress( f"Writing drop tables to file..."))

    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    f = open(dstPath, "w")
    for obj in objList:
        f.write(str(obj) + '\n')
    f.close()

    enemies = [obj for obj in objList if isinstance(obj, DropTableParser.Enemy)]
    
    with open(dstPath.replace(".txt", "_formatted.txt"), 'w') as formatted_file:
        written_tables = []
        
        enemies.sort(key=lambda x: x.name)
        for key, group in itertools.groupby(enemies, key=lambda x: x.name):
            sorted_levels = [item for item in group]
            sorted_levels.sort(key=lambda x: x.level)
            written_levels = []
            result = "{{Tabber"
            
            for dropper in sorted_levels:
                table_name = dropper.name.rstrip()
                
                if table_name != '' and dropper not in written_tables and dropper.level not in written_levels:
                    result += (f"\n|Level {dropper.level.replace('.0', '')}\n|")
                    result += dropper.to_wiki_format()
                    
                    written_levels.append(dropper.level)
                    written_tables.append(dropper)
            
            result += "\n}}\n\n"
            formatted_file.write(result)
    
    parser.on_progress_update(Progress( f"Finished parsing drop tables..."))

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

@LinkerRegistry.register("Items", [FileTags.Item, FileTags.PlaceableScript, FileTags.DecorationScript])
def linkItems(parser, srcPaths, dstPath):
    items = jsonParse(parser, srcPaths[FileTags.Item.value], ItemParser.getItem)
    parser.on_progress_update(Progress( f"Organizing {len(items)} items..."))
    logging.debug("Found " + str(len(items)) + " items.")
    
    items.sort(key=operator.attrgetter('gID'))
    
    written_items = []
    unique_items = []
    for item in items:
        name = re.sub(r"\((Up|L|R)\)", "", item.name).strip()
        if name not in written_items:
            unique_items.append(item)
            written_items.append(name)
    
    parser.on_progress_update(Progress( f"Finding item sprites..."))
    
    count = 0
    
    with open(parser.spritesPath, 'r') as sprites_file:
        sprites = sprites_file.readlines()
        for item in unique_items:
            count += 1
            if count % 100 == 0:
                parser.on_progress_update(Progress(f"Found sprites for {count}/{len(unique_items)}"))
                
            
            matching_sprite = None
            for x in sprites:
                if x.startswith(f"{item.icon_pID},"):
                    matching_sprite = x
                    break
            if matching_sprite is not None:
                item.icon_filepath = matching_sprite.split(',')[2].strip()
                
            if isinstance(item, ItemParser.Furniture):
                rotated_versions = [x for x in items if x.name == f"{item.name} (L)" or x.name == f"{item.name} (R)"]
                if rotated_versions:
                    item.rotateable = True
                    
                try:
                    set_candidates = [x.name for x in items if x.name.startswith(item.name.split(" ")[0]) and x.name != item.name]
                    if len(set_candidates) > 2:
                        set_name_length = len(set(item.name.split(" ")).intersection(set_candidates[1].split(" ")))
                        item.part_of_set = " ".join(item.name.split(" ")[0:(set_name_length - 1)])
                except:
                    logging.error(f"Error finding set for {item.name}", exc_info=True)               
                
    parser.on_progress_update(Progress( f"Writing items to file..."))
    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    f = open(dstPath, "w")
    for item in unique_items:
        f.write(str(item) + '\n')

    f.close()
    
    with open(dstPath.replace(".txt", "_description_template.txt"), 'w') as descriptions_file:
        unique_items.sort(key=lambda x: x.name)
        default = "    |#default=Edit in https://sun-haven.fandom.com/wiki/Template:Description <!--if the item doesn't have a listing here, it will show this-->}}\n"
        
        descriptions_file.write("<includeonly><!--1.2.0-->{{#switch:{{lc:{{#sub:{{{1|{{PAGENAME}}}}}|0|1}} }}\n")
        descriptions_file.write("<!-- example: |name(lower case letters)=Description -->\n")

        for key, group in itertools.groupby(unique_items, lambda x: x.name.strip().lower()[0]):
            descriptions_file.write(f"|{key}=" + "{{#switch:{{lc:{{{1|{{PAGENAME}}}}}}}\n")
            for shared_description_key, shared_descriptions in itertools.groupby(group, lambda x: x.description):
                item_names = set([x.name.lower() for x in shared_descriptions])
                clean_description = re.sub(r"<color=#[A-Z0-9]+>\([\w\s]+\)<\/color>", "", shared_description_key).replace("</b>", "'''").replace("<b>", "'''")
                clean_description = re.sub(r'\s{2,}', ' ', clean_description)
                
                if clean_description != "":
                    descriptions_file.write(f"    |{'|'.join(item_names)}={clean_description}\n")
            descriptions_file.write(default)
            
        descriptions_file.write("|#default=Edit in https://sun-haven.fandom.com/wiki/Template:Description")
        descriptions_file.write("}}</includeonly><noinclude>{{documentation}}</noinclude>")
    
    with open(dstPath.replace(".txt", ".csv"), 'w') as csvfile:
        item_writer = csv.writer(csvfile)
        for item in unique_items:
            item_writer.writerow(item.to_csv_list())
    
    with open(dstPath.replace(".txt", "_furniture.csv"), 'w') as furniture_file:
        furniture_writer = csv.writer(furniture_file)
        for item in unique_items:
            if isinstance(item, ItemParser.Furniture):
                furniture_writer.writerow(item.to_csv_list())
    
    parser.on_progress_update(Progress( f"Finished parsing items..."))

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

@LinkerRegistry.register("Gift Tables", [FileTags.GiftTable])
def linkGiftTables(parser: Parser, srcPaths, dstPath):
    objList = jsonParse(parser, srcPaths[FileTags.GiftTable.value], GiftTableParser.getGiftTable)
    logging.debug("Found " + str(len(objList)) + " Gift Tables.")

    
    datumList = []
    for o in objList:
        datumList.extend([x for x in o.love])
        datumList.extend([x for x in o.like])
        datumList.extend([x for x in o.good])
        datumList.extend([x for x in o.dislike])
        datumList.extend([x for x in o.unique])
    parser.assets_parser.csvParseAssetFile(datumList)
    
    parser.on_progress_update(Progress( f"Writing gift tables to file..."))
    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    f = open(dstPath, "w")
    for obj in objList:
        f.write(obj.filename + '\n')
        f.write('Love:\n')
        for item in obj.loveResponses:
            f.write(": " + item + '\n')
        for item in obj.love:
            f.write("- " + item.name + '\n')
            
        f.write('Like:\n')
        for item in obj.likeResponses:
            f.write(": " + item + '\n')
        for item in obj.like:
            f.write("- " + item.name + '\n')
            
        f.write('Good:\n')
        for item in obj.goodResponses:
            f.write(": " + item + '\n')
        for item in obj.good:
            f.write("- " + item.name + '\n')
            
        f.write('Dislike:\n')
        for item in obj.dislikeResponses:
            f.write(": " + item + '\n')
        for item in obj.dislike:
            f.write("- " + item.name + '\n')
            
        f.write('Unique:\n')
        for item in obj.unique:
            f.write("- " + item.name + ": " + item.response + '\n')

        f.write('Birthday:\n')
        f.write("Month/Day: " + obj.birthMonth + "/" + obj.birthDay + '\n')
        for item in obj.birthdayResponses:
            f.write("- " + item + '\n')
        f.write('\n')
    f.close()
    parser.on_progress_update(Progress( f"Finished writing gift tables to file..."))

@LinkerRegistry.register("Merchants", [FileTags.MerchantTable])
def linkMerchants(parser: Parser, srcPaths, dstPath):

    objList = jsonParse(parser, srcPaths[FileTags.MerchantTable.value], MerchantParser.getMerchant)

    logging.debug("Found " + str(len(objList)) + " Merchants.")

    parser.on_progress_update(Progress( f"Found " + str(len(objList)) + " Merchants."))
    
    datumList = []
    for o in objList:
        datumList.extend([x for x in o.items])
    parser.assets_parser.csvParseAssetFile(datumList)
    parser.on_progress_update(Progress( f"Writing merchants to file..."))
    
    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    # f = open(dstPath, "w")
    # for obj in objList:
    #     f.write(str(obj) + '\n')
    # f.close()
    parser.on_progress_update(Progress( f"Finished writing merchants to file..."))
    
    with open(dstPath.replace(".txt", "_formatted.txt"), "w") as formatted_file:
        for merchant in objList:
            formatted_file.write(f"\n{merchant.filename}")
            formatted_file.write("\n{{Shop/header|shop=SHOP NAME HERE}}")
            for item in merchant.items:
                formatted_file.write("\n{{Shop|" + f"{item.name}|{item.value}|{item.currency}" + "}}")
            formatted_file.write("\n{{Shop/footer}}\n")

@LinkerRegistry.register("Nested Recipe Lists", [FileTags.RecipeList])
def linkNestedRecipeLists(parser: Parser, srcPaths, dstPath):
    recipe_lists = jsonParse(parser, srcPaths[FileTags.RecipeList.value], RecipeListParser.getRecipeList)
    logging.debug("Found " + str(len(recipe_lists)) + " Recipe Lists.")
    
    parser.on_progress_update(Progress( f"Found {str(len(recipe_lists))} Recipe Lists."))

    recipe_list_datum = []
    for o in recipe_lists:
        recipe_list_datum.extend([x for x in o.items])
    parser.assets_parser.csvParseAssetFile(recipe_list_datum)
    
    recipe_paths = [x['filename'] for x in parser.assets_parser.csvParseMetadataFile(parser.dstPath) if 'recipe' in x['tags'] and '#' not in x['filename']]
    recipes = jsonParse(parser, recipe_paths, RecipeParser.getRecipe)
    logging.debug("Found " + str(len(recipes)) + " Recipes.")
    parser.on_progress_update(Progress( f"Found " + str(len(recipes)) + " Recipes."))

    recipe_datum = []
    recipe_refs_datum = []
    recipe_datum.extend([x.output for x in recipes])
    for rec in recipes:
        recipe_datum.extend([x for x in rec.inputs])
        recipe_refs_datum.extend([x for x in rec.required_progress])
        
    parser.assets_parser.csvParseAssetFile(recipe_datum)
    refs = parser.assets_parser.csvParseReferenceFile(recipe_refs_datum)

    parser.on_progress_update(Progress( f"Writing recipes to file..."))
    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    with open(dstPath.replace(".txt", "_formatted.txt"), "w") as formatted_file:
        for workbench in recipe_lists:
            matching_recipes = [r for r in recipes if str(r.name) in [str(x.name) for x in workbench.items]]
            logging.debug(f"Getting recipes for {workbench.filename} (found {len(matching_recipes)}/{len(workbench.items)} recipes)")
            for recipe in matching_recipes:
                workbench_name = workbench.filename
                workbench_name = re.sub(r'.*RecipeList_', '', workbench_name)
                workbench_name = re.sub(r'(#[0-9]+)*\.json', '', workbench_name)
                
                recipe.workbench = workbench_name.replace("RecipeList _", "")
                
                recipe_progress = []
                for progress in recipe.required_progress:
                    ref = [x for x in refs if progress.pID == x.pID][0]
                    recipe_progress.append(ref)
                recipe.required_progress = recipe_progress
                
                logging.debug(f"\twriting {recipe.name}")
                formatted_file.write(recipe.to_wiki_format())
            
        logging.debug("Getting Jam Recipes...")
        # Jam Maker doesn't have a recipe list ?????!!!?
        # Grabbing all recipes that have the word "Jam", avoiding things like "Jam Shed" and "Jam Maker"
        for recipe in [r for r in recipes if "Jam" in str(r.name) and not str(r.name).startswith("Jam")]:
                recipe.workbench = "Jam Maker"
                
                recipe_progress = []
                for progress in recipe.required_progress:
                    ref = [x for x in refs if progress.pID == x.pID][0]
                    recipe_progress.append(ref)
                recipe.required_progress = recipe_progress
                
                logging.debug(f"\twriting {recipe.name}")
                formatted_file.write(recipe.to_wiki_format())

    parser.on_progress_update(Progress( f"Finished recipes to file..."))

@LinkerRegistry.register("Recipe Lists", [FileTags.RecipeList])
def linkRecipeLists(parser: Parser, srcPaths, dstPath):
    objList = jsonParse(parser, srcPaths[FileTags.RecipeList.value], RecipeListParser.getRecipeList)
    logging.debug("Found " + str(len(objList)) + " Recipe Lists.")
    
    parser.on_progress_update(Progress( f"Found {str(len(objList))} Recipe Lists."))

    datumList = []
    for o in objList:
        datumList.extend([x for x in o.items])
    parser.assets_parser.csvParseAssetFile(datumList)
    
    parser.on_progress_update(Progress( f"Writing recipe lists to file..."))

    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    f = open(dstPath, "w")
    for obj in objList:
        f.write(obj.filename + '\n')
        for item in obj.items:
            f.write("- "+item.name + '\n')
        f.write('\n')
    f.close()
    parser.on_progress_update(Progress( f"Finished writing recipe lists to file..."))


@LinkerRegistry.register("Recipes", [FileTags.Recipe])
def linkRecipes(parser: Parser, srcPaths, dstPath):
            
    objList = jsonParse(parser, srcPaths[FileTags.Recipe.value], RecipeParser.getRecipe)
    logging.debug("Found " + str(len(objList)) + " Recipes.")
    parser.on_progress_update(Progress( f"Found " + str(len(objList)) + " Recipes."))
    

    datumList = []
    datumList.extend([x.output for x in objList])
    for o in objList:
        datumList.extend([x for x in o.inputs])
        datumList.extend([x for x in o.required_progress])
        
    datumList.extend([x.workbench for x in objList if x.workbench is not None])
    parser.assets_parser.csvParseAssetFile(datumList)

    parser.on_progress_update(Progress( f"Writing recipes to file..."))
    os.makedirs(os.path.dirname(dstPath), exist_ok=True)
    f = open(dstPath, "w")
    csv_file = open(dstPath.replace(".txt", ".csv"), "w")
    for recipe in objList:
        f.write(recipe.filename+'\n')

        if recipe.output.gID and recipe.output.name:
            if parser.gameVersion == "230405":
                jPath = os.path.join(parser.dataPath,'_Monobehaviour/Item', recipe.output.gID +' - '+ recipe.output.name + '.json')
            else:
                jPath = os.path.join(parser.dataPath,'Monobehaviour', recipe.output.gID+' - '+recipe.output.name+'.json')

            if os.path.isfile(jPath):
                j = open(jPath)
                data = json.load(j)
                f.write(': ' + data['description'] + '\n: ' + data['helpDescription']+'\n')
                recipe.output.sell_price = data['sellPrice']
                recipe.output.sell_type = "Coins"
                if data['orbsSellPrice'] > 0:
                    recipe.output.sell_price = data['orbsSellPrice']
                    recipe.output.sell_type = "Orbs"
                if data['ticketSellPrice'] > 0:
                    recipe.output.sell_price = data['ticketSellPrice']
                    recipe.output.sell_type = "Tickets"
                j.close()
        
        f.write('Crafting Time: '+recipe.craftTime+'\nInputs:\n')
        for item in recipe.inputs:
            f.write("- "+item.name + ': ' + item.amount + '\n')
        f.write('Output:\n- ' +
                recipe.output.name + ': ' + recipe.output.amount + '\n')
        f.write('\n')
        csv_file.write(recipe.to_csv() + "\n")
        
    csv_file.close()
    f.close()
    
    with open(dstPath.replace(".txt", "_formatted.txt"), "w") as formatted_file:
        for recipe in objList:
            formatted_file.write(recipe.to_wiki_format())

    parser.on_progress_update(Progress( f"Finished recipes to file..."))

@LinkerRegistry.register("Statted Items", [FileTags.Statted])
def linkStattedItems(parser, srcPaths, dstPath):
    objList = jsonParse(parser, srcPaths[FileTags.Statted.value], StattedItemParser.getStattedItem)
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
    
@LinkerRegistry.register("Quests", [FileTags.Quest])
def linkQuests(parser: Parser, srcPaths, dstPath):

    objList = jsonParse(parser, srcPaths[FileTags.Quest.value], QuestParser.getQuest)
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
