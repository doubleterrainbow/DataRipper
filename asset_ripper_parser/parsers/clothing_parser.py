import logging
import math
import os
import re

from asset_ripper_parser.index_files import FileIndexer
from asset_ripper_parser.models.clothing import (
    Clothing,
    clothing_colors,
    ClothingDirection,
    ClothingType,
)
from asset_ripper_parser.parse_exported_file import parse_exported_file
from asset_ripper_parser.parse_sprite_sheet import parse_sprite_asset, Sprite


def simplified_name(name: str) -> str:
    return name.lower().split("'", maxsplit=1)[0]


def parse_clothing(
    indexer: FileIndexer,
    item_paths: list[str],
    batch_size=500,
    on_batch_complete=None,
    report_progress=None,
):
    """Given a list of file paths, returns a list of items.

    Args:
        indexer (FileIndexer):  used to look up the icon/sprite for this item.
        item_paths (list[str]): all asset file paths with item information.
        batch_size (int): amount of files to parse before returning and purging current arrays. Defaults to 500.
        on_batch_complete (function, optional): Called when batch has been completed, returns list of items.
        report_progress (function, optional): Called when an item has been parsed. Defaults to None.
        parse_sprite (bool): If true, will look up sprite and apply it to the returned object. Defaults to False.
    """
    batch = 0
    max_batches = math.ceil(len(item_paths) / batch_size)

    while batch < max_batches:
        index_start = batch * batch_size
        index_end = index_start + batch_size

        logging.debug(
            "parsing batch %d / %d [%d:%d]",
            batch + 1,
            max_batches,
            index_start,
            index_end,
        )
        items = []

        for path in item_paths[index_start:index_end]:
            try:
                main_component = parse_exported_file(path)[0]["MonoBehaviour"]

                if (
                    # ("stats" in main_component and main_component["stats"]) or
                    "description" not in main_component
                    or not main_component["description"]
                ):
                    # logging.debug("Ignoring %s", os.path.basename(path))
                    continue

                full_name = main_component["name"]
                if "(" in full_name:
                    name_matches = re.search(r"([^(]+) \(([\w\s]+)\)", full_name)
                    base_name = name_matches.group(1).strip()
                    variant = name_matches.group(2)
                else:
                    base_name = full_name
                    variant = ""

                logging.debug(f"Found item = {base_name}, variant = {variant}")

                clothing = Clothing(name=base_name, color=variant)

                # layer_data_file = indexer.find_filepath_from_guid(
                #     main_component["clothingLayerData"]["guid"]
                # )
                # if layer_data_file:
                #     words_to_match = [
                #         os.path.basename(layer_data_file).replace(".asset", "")
                #     ]
                # else:
                words_to_match = [
                    simplified_name(word) for word in base_name.split(" ")
                ] + [variant.lower()]

                clothing.clothing_type = ClothingType.Shirt
                if "dress" in full_name.lower():
                    clothing.clothing_type = ClothingType.Dress
                elif "pant" in full_name.lower() or "jeans" in full_name.lower():
                    clothing.clothing_type = ClothingType.Pants
                elif (
                    "shirt" in full_name.lower()
                    or "chest" in full_name.lower()
                    or "coat" in full_name.lower()
                ):
                    clothing.clothing_type = ClothingType.Shirt
                elif "cape" in full_name.lower():
                    clothing.clothing_type = ClothingType.Cape
                elif "skirt" in full_name.lower():
                    clothing.clothing_type = ClothingType.Skirt
                elif "gloves" in full_name.lower():
                    clothing.clothing_type = ClothingType.Gloves
                elif "hat" in full_name.lower() or "helmet" in full_name.lower():
                    clothing.clothing_type = ClothingType.Hat

                icon_path = indexer.find_sprite_path_from_guid(
                    main_component["icon"]["guid"]
                )
                if icon_path is not None:
                    clothing.icon = parse_sprite_asset(indexer, icon_path)

                sprite_path = indexer.find_sprite_path_from_matcher(
                    lambda x: all(
                        [simplified_name(word) in x.lower() for word in words_to_match]
                    )
                    and not (
                        "sleeves" in x or "sleves" in x or "toparm" in x or "arms" in x
                    )
                    and not x == icon_path
                    and not x == icon_path.replace(".png", "_0.png")
                    # and clothing.clothing_type.value in x
                )
                # logging.debug(f"Found sprite: {sprite_path}")
                if sprite_path is not None:
                    clothing.sprite = parse_sprite_asset(indexer, sprite_path)

                    sleeves_path = indexer.find_sprite_path_from_matcher(
                        lambda x: (
                            all(
                                [
                                    simplified_name(word) in x.lower()
                                    for word in words_to_match
                                ]
                            )
                            and (
                                "sleeves" in x
                                or "sleves" in x
                                or "toparm" in x
                                or "arms" in x
                            )
                        )
                    )
                    # logging.debug(f"Found sleeves: {sleeves_path}")
                    if sleeves_path:
                        clothing.sleeves_sprite = parse_sprite_asset(
                            indexer, sleeves_path
                        )

                if report_progress is not None:
                    report_progress()
                items.append(clothing)
            except:
                logging.error("Could not parse %s", path, exc_info=True)

        if on_batch_complete is not None:
            on_batch_complete(batch, max_batches, items)

        batch += 1
