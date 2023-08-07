
from itertools import chain
import os
import logging
import pathlib

from DesktopApp.file_tags import FileTags
from DesktopApp.item_category import ItemCategory


class FileIndexer:
    def __init__(self, assets_folder, ids_file, file_tags_file):
        self.assets_folder = assets_folder
        self.ids_file = ids_file
        self.file_tags_file = file_tags_file
    
    def index_files(self, create_ids=True, organize_files=True):
        if create_ids:
            self._map_guids()
        if organize_files:
            self._organize_files()
        
    def ignore_file(self, filename) -> bool:
        return '.mat' in filename or '.anim' in filename or "Mesh_" in filename or \
            '.controller' in filename or '_tiles_' in filename or '_placeable' in filename

    def _map_guids(self):
        with open(self.ids_file, 'w') as ids_file:
            for path, subdirs, files in os.walk(self.assets_folder):
                for name in files:
                    if not name.endswith('.meta') or self.ignore_file(name):
                        continue
                    
                    with open(pathlib.PurePath(path, name), 'r') as meta_file:
                        meta_file_text = meta_file.readlines()
                        if 'guid:' in meta_file_text[1]:
                            logging.debug(f"Indexing {name}")
                            content_file_name = name.replace('.meta', '')
                            guid = meta_file_text[1].replace('guid:', '').strip()
                            ids_file.write(f"{content_file_name},{guid}\n")
                            
    def _organize_files(self):
        armor_types = ["chest", "pants", "gloves", "hat", "back", "ring", "amulet", "keepsake"]
        race_types = ["human", "elf", "amari", "naga", "elemental", "angel", "demon"]

        logging.debug('Reading all files')
        # self.on_progress_update(Progress(f"Reading all files. This will take a while to complete..."))
        
        progress_increment = 1000
        total_processed = 0
        
        with open(self.file_tags_file, 'w') as file_tags_file:
            subdirs = [x[0] for x in os.walk(self.assets_folder)]  
            for subdir in subdirs:
                if "MonoBehaviour" not in subdir and "PrefabInstance" not in subdir:
                    logging.debug(f"Skipping directory {subdir}")
                    continue
                files = os.walk(subdir).__next__()[2] 
                for filename in files:
                    total_processed += 1
                    if total_processed % progress_increment == 0:
                        logging.debug(f"Organized {total_processed} files...")
                    
                    filepath = os.path.join(self.assets_folder, subdir, filename)

                    is_unparseable_file = filename.endswith('.meta') or \
                        filename.endswith(".png") or filename.endswith(".dll") or filename.endswith(".ogg")
                    if is_unparseable_file or self.ignore_file(filename):
                        continue

                    tags = ""
                    logging.debug(f"Tagging {filename}...")
                    with open(filepath, encoding='utf-8') as inner_file:
                        try:
                            text = inner_file.read()

                            if 'id' in text and 'canSell: 1' in text:
                                tags += f",{FileTags.Item.value}"
                            if 'enemyName' in text:
                                tags += f",{FileTags.Enemy.value}"
                            if 'questName' in text:
                                tags += f",{FileTags.Quest.value}"
                            # if 'category' in text:
                            #     tags += f",{ItemCategory.from_index(data['category']).value}"
                            if 'armorType' in text:
                                # if data['armorType'] <= 4:
                                #     if 'stats' in data and len(data['stats']) > 0:
                                #         tags += ",armor"
                                #     else:
                                #         tags += ",clothing"
                                # tags += "," + armor_types[data['armorType']]
                                tags += f',{FileTags.Clothing.value}'
                            if 'stats' in text:
                                tags += f",{FileTags.Statted.value}"
                            if 'availableAtCharacterSelect' in text:
                                tags += f",{FileTags.CharacterCustomization.value}"
                            # if 'availableRaces' in text:
                            #     for r in text['availableRaces']:
                            #         tags += "," + race_types[r]
                            if '_clothingLayerInfo' in text:
                                tags += ",sprite list"
                            if 'canDropRustyKey' in text:
                                tags += ",mine"
                            if 'dungeonEntrance' in text:
                                tags += ",dungeon floor"
                            if 'lockedText' in text:
                                tags += ",dungeon chest"
                            if 'animalName' in text:
                                tags += ",animal"
                            if 'bundle' in text:
                                tags += ",museum bundle"
                            if 'interactiveText' in text and 'Bee Hive Box' in text:
                                tags += ",beehive box"
                            if 'bookName' in text:
                                tags += ",book"
                            if 'text' in text:
                                tags += ",readable"
                            if 'npc' in text:
                                tags += ",npc"
                            if 'love' in text:
                                tags += ",gift table"
                            if 'startingItems' in text:
                                tags += f",{FileTags.MerchantTable.value}"
                            if 'input' in text and 'output' in text:
                                tags += f",{FileTags.Recipe.value}"
                            if 'craftingRecipes' in text:
                                tags += f",{FileTags.RecipeList.value}"
                            if '_drops:' in text or '_foliage' in text:
                                tags += f",{FileTags.DropTable.value}"
                            if 'drops:' in text:
                                tags += f",{FileTags.Destructible.value}"
                            if 'fish:' in text:
                                if 'large' in text:
                                    tags += f",{FileTags.FishNet.value}"
                                else:
                                    tags += f",{FileTags.FishSpawner.value}"
                            if 'cropStages' in text:
                                tags += f",{FileTags.Seed.value}"
                            if 'placeableOnTables' in text:
                                tags += f",{FileTags.DecorationScript.value}"
                            if '_canDestroyDecorations' in text:
                                tags += f",{FileTags.PlaceableScript.value}"

                        except:
                            logging.error(f"Unable to parse {filename}", exc_info=True)
                            tags = ""
                            
                    if tags != "":
                        
                        file_tags_file.write(subdir + os.sep + filename + tags +'\n')

    def _relevant_filepaths(self):
        return chain(os.walk(os.path.join(self.assets_folder, "MonoBehaviour")), os.walk(os.path.join(self.assets_folder, "PrefabInstance")))