from itertools import chain
import os
import logging
import pathlib
import re

from DesktopApp.file_tags import FileTags
from DesktopApp.item_category import ItemCategory
from DesktopApp.progress import Progress


class FileIndexer:
    def __init__(self, assets_folder, ids_file, file_tags_file):
        self.assets_folder = assets_folder
        self.ids_file = ids_file
        self.sprite_ids_file = ids_file.replace(".csv", "_sprites.csv")
        self.texture_ids_file = ids_file.replace(".csv", "_textures.csv")
        self.file_tags_file = file_tags_file

        self.folders_to_index = [
            "MonoBehaviour",
            "Resources",
            "PrefabInstance",
        ]  # maybe add 'Sprite'?

    def _get_path_from_guid(self, file, guid):
        """Searches file for text

        Args:
            file (str): File path to search within
            guid (str): Text to search for, assumed to follow ','

        Returns:
            str: File path aligned with guid
            None: if guid not in file
        """
        with open(file, "r", encoding="utf-8") as ids_file:
            for line in ids_file:
                if f",{guid}" in line:
                    return line.split(",")[0]

        return None

    def find_texture_path_from_guid(self, guid):
        return self._get_path_from_guid(self.texture_ids_file, guid)

    def find_sprite_path_from_guid(self, guid):
        return self._get_path_from_guid(self.sprite_ids_file, guid)

    def find_filepath_from_guid(self, guid):
        return self._get_path_from_guid(self.ids_file, guid)

    def find_name_from_guid(self, guid):
        with open(self.ids_file, "r", encoding="utf-8") as ids_file:
            while True:
                line = ids_file.readline()
                if not line:
                    break

                if f",{guid}" in line:
                    dirty_name = line.split(",")[0].split("\\")[-1]
                    return re.sub(r"[0-9]+ - (.+)\.asset", "\\1", dirty_name).replace(
                        ".asset", ""
                    )

        return "unknown"

    def get_asset_count(self) -> int:
        files, folders = self._count_files(self.assets_folder)
        return files

    def index_files(self, create_ids=True, organize_files=True):
        if create_ids:
            self._map_guids()
        if organize_files:
            self._organize_files()

    def create_mapping_files(self, report_progress=None):
        self._map_guids(report_progress=report_progress)

    def create_organization_file(self, report_progress=None):
        self._organize_files(report_progress=report_progress)

    def ignore_file(self, filename) -> bool:
        return (
            ".mat" in filename
            or ".anim" in filename
            or "Mesh_" in filename
            or ".controller" in filename
            or "_tiles_" in filename
        )

    def _count_files(self, dir_path):
        folder_array = os.scandir(dir_path)
        files = 0
        folders = 0
        for path in folder_array:
            if path.is_file():
                files += 1
            elif path.is_dir():
                folders += 1
                file_count, folder_count = self._count_files(path)
                files += file_count
                folders += folder_count
        return files, folders

    def _map_guids(self, report_progress=None):
        count = 0
        increment = 1000

        with open(self.ids_file, "w", encoding="utf-8") as ids_file:
            with open(self.sprite_ids_file, "w", encoding="utf-8") as sprite_ids_file:
                with open(
                    self.texture_ids_file, "w", encoding="utf-8"
                ) as texture_ids_file:
                    for path, _, files in os.walk(self.assets_folder):
                        for name in files:
                            count += 1
                            if count % increment == 0 and report_progress is not None:
                                report_progress()

                            if not name.endswith(".meta") or self.ignore_file(name):
                                continue

                            is_sprites_file = "Sprite" in path or (
                                "icon" in name and ".asset" in name
                            )
                            is_texture_file = ".png" in name
                            is_data_file = [
                                x for x in self.folders_to_index if x in path
                            ]

                            is_valid_file = (
                                is_data_file or is_sprites_file or is_texture_file
                            )

                            if not is_valid_file:
                                # logging.debug(f"Skipping {name}")
                                continue

                            filepath = pathlib.PurePath(path, name)
                            with open(filepath, "r", encoding="utf-8") as meta_file:
                                meta_file_text = meta_file.readlines()
                                if "guid:" in meta_file_text[1]:
                                    # logging.debug(f"Indexing {name}")
                                    guid = (
                                        meta_file_text[1].replace("guid:", "").strip()
                                    )

                                    if is_sprites_file:
                                        image_path = str(filepath).replace(".meta", "")
                                        sprite_ids_file.write(f"{image_path},{guid}\n")
                                    elif is_texture_file:
                                        image_path = str(filepath).replace(".meta", "")
                                        texture_ids_file.write(f"{image_path},{guid}\n")
                                    else:
                                        asset_path = str(filepath).replace(".meta", "")
                                        ids_file.write(f"{asset_path},{guid}\n")

    def _organize_files(self, report_progress=None):
        armor_types = [
            "chest",
            "pants",
            "gloves",
            "hat",
            "back",
            "ring",
            "amulet",
            "keepsake",
        ]
        race_types = ["human", "elf", "amari", "naga", "elemental", "angel", "demon"]

        logging.debug("Reading all files")
        # self.on_progress_update(Progress(f"Reading all files. This will take a while to complete..."))

        progress_increment = 1000
        total_processed = 0

        with open(self.file_tags_file, "w") as file_tags_file:
            subdirs = [x[0] for x in os.walk(self.assets_folder)]
            for subdir in subdirs:
                if not [x for x in self.folders_to_index if x in subdir]:
                    logging.debug(f"Skipping directory {subdir}")
                    continue
                files = os.walk(subdir).__next__()[2]
                for filename in files:
                    total_processed += 1
                    if (
                        total_processed % progress_increment == 0
                        and report_progress is not None
                    ):
                        report_progress()

                    filepath = os.path.join(self.assets_folder, subdir, filename)

                    is_unparseable_file = (
                        filename.endswith(".meta")
                        or filename.endswith(".png")
                        or filename.endswith(".dll")
                        or filename.endswith(".ogg")
                    )
                    if (
                        is_unparseable_file
                        or self.ignore_file(filename)
                        or "_0" in filename
                    ):
                        continue

                    try:
                        tags = ""
                        check_file_contents = True
                        # logging.debug(f"Tagging {filename}...")

                        # if subdir.endswith('Sprite'):
                        #     tags += f",{FileTags.Sprite.value}"
                        #     file_tags_file.write(subdir + os.sep + filename + tags +'\n')
                        #     continue

                        if (
                            re.match(r"[0-9]{3,5} - .+[^(_0)]\.asset", filename)
                            is not None
                        ):
                            tags += f",{FileTags.Item.value}"
                        if "GiftTable" in filename:
                            tags += f",{FileTags.GiftTable.value}"
                            check_file_contents = False
                        if re.match(r"Recipe [0-9]+", filename) is not None:
                            tags += f",{FileTags.Recipe.value}"
                        if "RecipeList" in filename:
                            tags += f",{FileTags.RecipeList.value}"
                            check_file_contents = False
                        if "(Up)" in filename or "(L)" in filename or "(R)" in filename:
                            tags += f",{FileTags.Rotated.value}"
                        if "SkillTree.asset" in filename:
                            tags += f",{FileTags.SkillTree.value}"
                            check_file_contents = False
                        # if "_placeable.prefab" in filename: # this doesn't work (???)
                        #     tags += f",{FileTags.Placeable.value}"

                        if check_file_contents:
                            with open(filepath, encoding="utf-8") as inner_file:
                                try:
                                    text = inner_file.read()
                                    if "_hasAttack: 1" in text:
                                        tags += f",{FileTags.Enemy.value}"
                                    if "questName" in text:
                                        tags += f",{FileTags.Quest.value}"
                                    if "category" in text:
                                        category = re.search(r"category: ([0-5])", text)
                                        if category is not None:
                                            tags += f",{ItemCategory.from_index(int(category.group(1))).value}"
                                    if "armorMaterial: 1" in text:
                                        tags += f",{FileTags.Armor.value}"
                                    if "armorMaterial: 0" in text:
                                        tags += f",{FileTags.Clothing.value}"
                                    if "stats" in text:
                                        tags += f",{FileTags.Statted.value}"
                                    if "availableAtCharacterSelect" in text:
                                        tags += (
                                            f",{FileTags.CharacterCustomization.value}"
                                        )
                                    # if 'availableRaces' in text:
                                    #     for r in text['availableRaces']:
                                    #         tags += "," + race_types[r]
                                    # if '_clothingLayerInfo' in text:
                                    #     tags += ",sprite list"
                                    if "canDropRustyKey" in text:
                                        tags += ",mine"
                                    if "dungeonEntrance" in text:
                                        tags += ",dungeon floor"
                                    if "lockedText" in text:
                                        tags += ",dungeon chest"
                                    if "animalName" in text:
                                        tags += ",animal"
                                    if "bundle" in text:
                                        tags += ",museum bundle"
                                    if (
                                        "interactiveText" in text
                                        and "Bee Hive Box" in text
                                    ):
                                        tags += ",beehive box"
                                    if "bookName" in text:
                                        tags += ",book"
                                    # if 'text' in text:
                                    #     tags += ",readable"
                                    if "npc" in text:
                                        tags += ",npc"
                                    if "startingItems" in text:
                                        tags += f",{FileTags.MerchantTable.value}"
                                    if "_drops:" in text or "_foliage" in text:
                                        tags += f",{FileTags.DropTable.value}"
                                    if "drops:" in text:
                                        tags += f",{FileTags.Destructible.value}"
                                    if "fish:" in text:
                                        if "large" in text:
                                            tags += f",{FileTags.FishNet.value}"
                                        else:
                                            tags += f",{FileTags.FishSpawner.value}"
                                    if "cropStages" in text:
                                        tags += f",{FileTags.Seed.value}"
                                    if "progressID" in text:
                                        tags += f",{FileTags.Progress.value}"
                                    if "nodePoints:" in text:
                                        tags += f",{FileTags.Skill.value}"
                                    if "placeableOnTables:" in text:
                                        tags += f",{FileTags.Decoration.value}"
                                    if "wallpaper:" in text:
                                        tags += f",{FileTags.Wallpaper.value}"
                                    if (
                                        "useAbleByPlayer: 1" in text
                                        and "_decoration:" in text
                                        and "_itemData:" in text
                                    ):
                                        tags += f",{FileTags.Placeable.value}"

                                except:
                                    logging.error(
                                        f"Unable to parse {filename}", exc_info=True
                                    )
                                    tags = ""

                        if tags != "":
                            file_tags_file.write(
                                subdir + os.sep + filename + tags + "\n"
                            )
                    except:
                        logging.error(
                            f"Unable to open {filename} at {subdir}", exc_info=True
                        )

    def _relevant_filepaths(self):
        return chain(
            os.walk(os.path.join(self.assets_folder, "MonoBehaviour")),
            os.walk(os.path.join(self.assets_folder, "PrefabInstance")),
        )
