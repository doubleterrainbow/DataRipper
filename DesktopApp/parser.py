# import required module
from operator import truediv
import re
import os
import xml.etree.ElementTree as ET
import math
import time
import json
import logging
from asset_ripper_parser.file_tags import FileTags
from DesktopApp.item_category import ItemCategory
from DesktopApp.datum import Datum
from assets_parser import AssetsParser
from DesktopApp.progress import Progress

class Parser:
    def __init__(self, 
                game_version, 
                data_path,
                code_path,
                output_path, 
                on_progress_update, 
                skip_setup=False
                ) -> None:
        self.gameVersion = game_version
        
        self.on_progress_update = on_progress_update
        
        self.codePath = f"{code_path}/SunHaven.Core/Wish"
        self.dataPath = data_path

        self.xmlPath = f'{data_path}/assets.xml'
        self.csvPath = f'{data_path}/assets.csv'
        self.refPath = f'{data_path}/references.csv'
        self.spritesPath = f'{data_path}/sprites.csv'
        self.assets_parser = AssetsParser(self.csvPath, self.xmlPath, self.refPath, on_progress_update)
        
        if not skip_setup:
            self.xml2csv(self.xmlPath, self.csvPath, self.refPath, self.spritesPath)

        self.outputPath = output_path
        self.dstPath = os.path.join(output_path, game_version, 'fileTypes.csv')
        os.makedirs(os.path.join(output_path, game_version), exist_ok=True)
        
        if not skip_setup:
            self.labelFiles(f"{data_path}/MonoBehaviour", self.dstPath)

    
    def xml2csv(self, srcPath, assets_csv, references_path, sprites_path):
        logging.debug('Opening assets.xml')
        self.on_progress_update(Progress("Viewing GIGANTIC list of assets..."))
        tree = ET.parse(srcPath)
        root = tree.getroot()

        elementCount = sum(1 for _ in root)
        increment = math.ceil(elementCount / 20)

        objList = []
        references = []
        sprites = []

        logging.debug("Parsing assets.xml")
        # all items data
        count = 0
        total_processed = 0
        for elem in root:
            total_processed += 1
            count += 1
            if count >= increment:
                self.on_progress_update(Progress(f"Scanned {total_processed}/{elementCount} assets..."))
                count = 0
                logging.debug(f"Scanned {total_processed}/{elementCount} assets...")

            container = elem.find('Container')
            is_progress_container = container is not None and container.text is not None and 'progress' in container.text

            pID = elem.find('PathID').text
            gID = ""
            name = ""
            data = elem.find('Name').text.split(' - ')
            if len(data) > 1:
                gID = data[0]
                name = data[1]
            else:
                name = data[0]
                
            if gID:
                objList.append(Datum(pID, gID, name))
            
            if re.match("[A-Za-z]+FishSpawner.*", name) is not None or \
                is_progress_container or name.startswith('RecipeList_'):
                references.append(Datum(pID, "0", name))
            
            name = elem.find('Name').text
            type = elem.find('Type')
            if type is not None and type.text == "Sprite":
                sprites.append(Datum(pID, "0", name))
                
        logging.debug("\nSorting")
        objList.sort()

        logging.debug("Writing to Disk")
        
        os.makedirs(self.dataPath, exist_ok=True)
        f = open(assets_csv, "w")
        for obj in objList:
            f.write(str(obj) + '\n')
        f.close()
        
        # Write references - Fish spawns, Recipes lists, Skills, Game Progress, and Quest Markers
        with open(references_path, "w") as reference_file:
            for obj in references:
                reference_file.write(str(obj) + '\n')
        
        # Write sprite names for image lookup
        with open(sprites_path, "w") as sprites_file:
            for sprite in sprites:
                sprites_file.write(str(sprite) + '\n')
        
    def labelFiles(self, srcPath, dstPath):
        def isFileType(f, types):
            name = os.path.basename(f)
            for datatype in types:
                if name.startswith(datatype):
                    return True
            return False

        tic = time.perf_counter()
        
        logging.debug('Reading all files')
        self.on_progress_update(Progress(f"Reading all files. This will take a while to complete..."))

        files = [os.path.join(dir_path, file) for dir_path, dn, file_names in os.walk(srcPath) for file in file_names]

        file_count = len(files)
        progress_increment = math.ceil(file_count / 20)
        count = 0

        armorTypes = ["chest", "pants", "gloves", "hat", "back", "ring", "amulet", "keepsake"]
        raceTypes = ["human", "elf", "amari", "naga", "elemental", "angel", "demon"]

        dataTypes = ['DataTile', 'Entity', 'MeshGenerator', 'AIAnimationTester', 'AnimationHandler', 'AnimationIndex', 'BlockedZoneTrigger', 'ClifMaker', 'DebugUIHandler']
        ambianceTypes = ['Plant', 'RendererShadows', 'AmbientLightZone', 'AmbientSound', 'CloudsMoving', 'LightFlicker', 'DecorativeTree', 'BigTree', 'LightGlow']
        uiTypes = ['Image', 'ActionBarIcon', 'AdaptiveUIScale', 'AnimalCanvas', 'AnimalNamingCanvas', 'CameraBounds', 'CameraController', 'CameraDrone', 'CameraZone', \
            'CanvasScalar', 'CarnivalShopMoneyUI', 'CatenaryLineRenderer', 'CinematicCamera', 'ClothingColorButton', 'ClothingImageButton', 'CommunityTokenMoneyUI', \
            'ContentSizeFitter', 'CraftingNotificationBubble', 'CraftingPanel', 'CraftingTable', 'CraftingTab', 'CraftingUI', 'CurrencyDepositButton', \
            'CustomCurrencyMoneyUI', 'NavigationElement', 'TextMeshProUGUI', 'Slot', 'Button', 'TMP_SubMeshUI', 'TextSizer', 'ItemImage', 'Popup', 'OnHovor', \
            'DOTweenAnimation', 'Canvas', 'UIButton', 'Slider']

        logging.debug(file_count)

        logging.debug("Parsing Asset Database")
        
        total_processed = 0
        with open(dstPath, "w") as label_file:
            for filePath in files:
                count += 1
                total_processed += 1
                if count >= progress_increment:
                    self.on_progress_update(Progress(f"Scanned {total_processed}/{file_count} files..."))
                    count = 0
                    logging.debug(f"Scanned {total_processed}/{file_count} files...")
                
                filename = os.path.relpath(filePath, os.path.join(srcPath,'..'))

                if not filename.endswith('.json'):
                    continue

                if isFileType(filename, dataTypes):
                    label_file.write(filename + ',trash,data\n')
                    continue

                if isFileType(filename, ambianceTypes):
                    label_file.write(filename + ',trash,ambiance\n')
                    continue

                if isFileType(filename, uiTypes):
                    label_file.write(filename + ',trash,ui element\n')
                    continue

                tags = ""
                with open(filePath) as inner_file:
                    try:
                        data = json.load(inner_file)

                        if 'id' in data and 'canSell' in data:
                            tags += ",item"
                        if 'enemyName' in data and data['enemyName']:
                            tags += ",enemy"
                        if 'questName' in data and isinstance(data['questName'], str):
                            tags += ",quest"
                        if 'category' in data:
                            tags += f",{ItemCategory.from_index(data['category']).value}"
                        if 'armorType' in data:
                            if data['armorType'] <= 4:
                                if 'stats' in data and len(data['stats']) > 0:
                                    tags += ",armor"
                                else:
                                    tags += ",clothing"
                            tags += ","+armorTypes[data['armorType']]
                        if 'stats' in data and len(data['stats']) > 0:
                            tags += ",statted"
                        if 'availableAtCharacterSelect' in data:
                            tags += ",character customization"
                        if 'availableRaces' in data:
                            for r in data['availableRaces']:
                                tags += "," + raceTypes[r]
                        if '_clothingLayerInfo' in data:
                            tags += ",sprite list"
                        if 'canDropRustyKey' in data:
                            tags += ",mine"
                        if 'dungeonEntrance' in data:
                            tags += ",dungeon floor"
                        if 'lockedText' in data:
                            tags += ",dungeon chest"
                        if 'animalName' in data:
                            tags += ",animal"
                        if 'bundle' in data:
                            tags += ",museum bundle"
                        if 'interactiveText' in data and data['interactiveText'] == 'Bee Hive Box':
                            tags += ",beehive box"
                        if 'bookName' in data:
                            tags += ",book"
                        if 'text' in data and data['text']:
                            tags += ",readable"
                        if 'npc' in data and data['npc']:
                            tags += ",npc"
                        if 'love' in data and data['love']:
                            tags += ",gift table"
                        if 'startingItems' in data:
                            tags += f",{FileTags.MerchantTable.value}"
                        if 'input' in data and 'output' in data:
                            tags += f",{FileTags.Recipe.value}"
                        if 'craftingRecipes' in data and data['craftingRecipes']:
                            tags += f",{FileTags.RecipeList.value}"
                        if ('_drops' in data and data['_drops'] and 'drops' in data['_drops'][0] and data['_drops'][0]['drops']) or \
                            ('_foliage' in data and data['_foliage'] and 'drops' in data['_foliage']):
                            tags += f",{FileTags.DropTable.value}"
                        if ('drops' in data and 'drops' in data['drops']):
                            tags += f",{FileTags.Destructible.value}"
                        if 'fish' in data and data['fish'] and 'drops' in data['fish'] and data['fish']['drops']:
                            if 'large' in data:
                                tags += f",{FileTags.FishNet.value}"
                            else:
                                tags += f",{FileTags.FishSpawner.value}"
                        if 'cropStages' in data:
                            tags += f",{FileTags.Seed.value}"

                    except:
                        tags = ",unparseable"

                label_file.write(filename + tags +'\n')

        toc = time.perf_counter()
        logging.debug(f"Read all files in {toc - tic:0.4f} seconds")


