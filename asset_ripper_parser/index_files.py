"""Contains functionality for storing references to assets so they can be quickly parsed."""
import csv
import os
import logging
import pathlib
import re
from asset_ripper_parser import file_tags


class FileIndexer:
    """
    Mostly a utility class, this supports parsing functionality by holding references
    to the files which map file IDs to their paths. It also categorizes files so we know
    which file paths refer to a specific type of in-game content.
    """

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
            "Scenes",
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
            ids_reader = csv.reader(ids_file)
            for line in ids_reader:
                if len(line) > 1 and line[1] == guid:
                    return line[0]

        return None

    def find_texture_path_from_guid(self, guid) -> str:
        """
        Searches Texture GUIDs to find the path to the PNG

        Args:
            guid (str): the ID of the file to find

        Returns:
            str: File path of asset with given GUID
            None: GUID has not been mapped to a file path
        """
        return self._get_path_from_guid(self.texture_ids_file, guid)

    def find_sprite_path_from_guid(self, guid):
        """
        Searches Sprite GUIDs to find the path to the .asset file

        Args:
            guid (str): the ID of the file to find

        Returns:
            str: File path of asset with given GUID
            None: GUID has not been mapped to a file path
        """
        return self._get_path_from_guid(self.sprite_ids_file, guid)

    def find_filepath_from_guid(self, guid):
        """
        Searches asset GUIDs to find the path to the file.
        This file will usually be a .asset file or a .prefab file.

        Args:
            guid (str): the ID of the file to find

        Returns:
            str: File path of asset with given GUID
            None: GUID has not been mapped to a file path
        """
        return self._get_path_from_guid(self.ids_file, guid)

    def find_name_from_guid(self, guid):
        """
        Searches asset GUIDs for a filepath, and extrapolates the
        name of the file from the path.

        Args:
            guid (str): the ID of the file to find

        Returns:
            str: Name of the file (without extension) assigned to the given GUID
            None: GUID has not been mapped to a file path
        """
        with open(self.ids_file, "r", encoding="utf-8") as ids_file:
            ids_reader = csv.reader(ids_file)
            for line in ids_reader:
                if len(line) > 1 and line[1] == guid:
                    dirty_name = os.path.basename(line[0])
                    return re.sub(r"[0-9]+ - (.+)\.asset", "\\1", dirty_name).replace(
                        ".asset", ""
                    )

        return "unknown"

    def get_asset_count(self) -> int:
        """
        Returns the amount of files in the provided asset folder

        Returns:
            ing: amount of files in assets_folder
        """
        files, _ = self._count_files(self.assets_folder)
        return files

    def create_mapping_files(self, report_progress=None):
        """
        Creates csv files for assets, sprites, and textures.
        Each line in the CSV contains a file path and GUID for the file.

        Args:
            report_progress (function, optional): Runs every 1000 files that have been identified.
                                                    Defaults to None.
        """
        self._map_guids(report_progress=report_progress)

    def create_organization_file(self, report_progress=None):
        """
        Creates csv file of file paths and any types associated with that file.
        This categorizes files to more quickly provide file paths for a
        type of file (see file_tags)

        Args:
            report_progress (function, optional): Runs after each directory has been processed.
                                                    Defaults to None.
        """
        self._organize_files(report_progress=report_progress)

    def ignore_file(self, filename: str) -> bool:
        """
        Given a string, returns whether that is an irrelevant file.

        Args:
            filename (str): Name of the file to process

        Returns:
            bool: True if the file should be ignored,
                  False if it may be useful.

        """
        return (
            ".mat" in filename
            or ".anim" in filename
            or "Mesh_" in filename
            or ".controller" in filename
            or "_tiles_" in filename
        )

    def _count_files(self, dir_path: str) -> (int, int):
        """
        An efficient method to scan a directory and its subdirectory
        to determine the amount of folders and files it contains.

        Args:
            dir_path (str): the path of a directory to search within

        Returns:
            (int, int): (amount of files, amount of folders) in given path
        """
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
        """
        Business logic for mapping GUIDs to file paths

        Args:
            report_progress (function, optional): Runs every 1000 files processed. Defaults to None.
        """
        count = 0
        increment = 1000

        with open(self.ids_file, "w", encoding="utf-8") as ids_file:
            ids_csv_writer = csv.writer(ids_file)
            with open(self.sprite_ids_file, "w", encoding="utf-8") as sprite_ids_file:
                sprite_ids_csv_writer = csv.writer(sprite_ids_file)
                with open(
                    self.texture_ids_file, "w", encoding="utf-8"
                ) as texture_ids_file:
                    texture_ids_csv_writer = csv.writer(texture_ids_file)
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

                            is_useless_sprite = [
                                x
                                for x in [
                                    "crabs",
                                    "haircuts",
                                    "hair",
                                    "custom",
                                    "environment",
                                    "eyes",
                                    "floor_",
                                    "hat_",
                                    "tile",
                                    "Kpops",
                                    "legs_",
                                    "face",
                                    "shirt_",
                                    "sleeves_",
                                    "sleves_",
                                    "tail_",
                                    "grass",
                                    "Legs",
                                    "pants_",
                                    "Facial",
                                    "rock",
                                    "toparm",
                                    "chest_",
                                    "Amari",
                                ]
                                if x in name
                            ]

                            is_texture_file = ".png" in name
                            is_data_file = [
                                x for x in self.folders_to_index if x in path
                            ]

                            is_valid_file = (
                                is_data_file
                                or (is_sprites_file and not is_useless_sprite)
                                or is_texture_file
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
                                        sprite_ids_csv_writer.writerow(
                                            [image_path, guid]
                                        )
                                    elif is_texture_file:
                                        image_path = str(filepath).replace(".meta", "")
                                        texture_ids_csv_writer.writerow(
                                            [image_path, guid]
                                        )
                                    else:
                                        asset_path = str(filepath).replace(".meta", "")
                                        ids_csv_writer.writerow([asset_path, guid])

    def _determine_tags(self, filename: str, filepath: str) -> list[str]:
        """Reads filename and filepath and applies correct labels to

        Args:
            filename (str): name of the file to read
            filepath (str): path to open file contents

        Returns:
            list[str]: tags relevant to file
        """
        tags = []
        # logging.debug(f"Tagging {filename}...")

        for tag in file_tags.file_tags:
            if tag.filename_matcher is not None and tag.filename_matcher(filename):
                tags.append(tag.label.value)

        for tag in file_tags.file_tags:
            if tag.text_matcher is not None:
                with open(filepath, encoding="utf-8") as inner_file:
                    try:
                        if tag.text_matcher(inner_file.read()):
                            tags.append(tag.label.value)

                    except:
                        logging.error("Unable to parse %s", filename, exc_info=True)

        return tags

    def _organize_files(self, report_progress=None):
        """
        Determines category of files in asset folder based on its
        name and text inside.

        Args:
            report_progress (function, optional): Runs after every folder is processed. Defaults to None.
        """
        logging.debug("Reading all files")

        with open(self.file_tags_file, "w", encoding="utf-8") as file_tags_file:
            csv_writer = csv.writer(file_tags_file)
            subdirs = [x[0] for x in os.walk(self.assets_folder)]
            for subdir in subdirs:
                if report_progress is not None:
                    report_progress()

                if not [x for x in self.folders_to_index if x in subdir]:
                    logging.debug("Skipping directory %s", subdir)
                    continue

                files = os.walk(subdir).__next__()[2]
                for filename in files:
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
                        tags = self._determine_tags(filename, filepath)

                        if tags:
                            file_path = os.path.join(subdir, filename)
                            csv_writer.writerow([file_path] + tags)
                    except:
                        logging.error(
                            "Unable to open %s at %s", filename, subdir, exc_info=True
                        )
