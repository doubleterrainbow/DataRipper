import logging
import os.path
import pprint

from asset_ripper_parser.index_files import FileIndexer
from asset_ripper_parser.models.fish_spawn import FishSpawn, FishDrop
from asset_ripper_parser.models.item import Item
from asset_ripper_parser.parse_exported_file import parse_exported_file
from asset_ripper_parser.parsers.item_parser import parse_item
from asset_ripper_parser.utils import camel_case_split


def parse_fish_drops(
    indexer: FileIndexer, drops: list[dict], season: str, location: str
):
    fishes = []
    for drop in drops:
        fish = FishDrop()
        item_filepath = indexer.find_filepath_from_guid(drop["fish"]["guid"])
        item_component = parse_exported_file(item_filepath)[0]["MonoBehaviour"]
        item = Item(item_component["name"])
        fish.item = parse_item(indexer, item_component, item)
        fish.chance = drop["dropChance"]
        fish.season = season

        possible_locations = [
            "Farm",
            "Forest",
            "Town",
            "Sea",
            "Sewer",
            "Wilderness",
        ]
        matching_location = [
            x for x in possible_locations if x.lower() in location.lower()
        ]
        if matching_location:
            fish.location = matching_location[0]
        elif "Beach" in location:
            fish.location = "Sea"
        elif "Wishingwell" in location:
            fish.location = "Midnight Isle"
        else:
            fish.location = location

        fishes.append(fish)
    return fishes


def parse_fish_spawners(
    indexer: FileIndexer,
    item_paths: list[str],
    report_progress=None,
) -> list[FishSpawn]:
    """Given a list of file paths, returns a list of fish spawners.

    Args:
        indexer (FileIndexer):  used to look up the icon/sprite for this item.
                                Currently not doing that.
        item_paths (list[str]): all asset file paths with item information.
        report_progress (function, optional): Called when an item has been parsed. Defaults to None.

    Returns:
        list[Item]: List of parsed items.
    """
    spawners = []
    for path in item_paths:
        try:
            spawner_component = parse_exported_file(path, only_with_text="fish:")
            main_component = spawner_component[0]["MonoBehaviour"]

            spawner = FishSpawn()
            filename = os.path.basename(path)
            spawner.location_name = camel_case_split(filename.replace(".unity", ""))

            spawner.drops = parse_fish_drops(
                indexer, main_component["fish"]["drops"], "All", spawner.location_name
            )
            if main_component["hasSeasonalFish"] > 0:
                spawner.spring_drops = parse_fish_drops(
                    indexer,
                    main_component["fishSpring"]["drops"],
                    "Spring",
                    spawner.location_name,
                )

                spawner.summer_drops = parse_fish_drops(
                    indexer,
                    main_component["fishSummer"]["drops"],
                    "Summer",
                    spawner.location_name,
                )

                spawner.fall_drops = parse_fish_drops(
                    indexer,
                    main_component["fishFall"]["drops"],
                    "Fall",
                    spawner.location_name,
                )

                spawner.winter_drops = parse_fish_drops(
                    indexer,
                    main_component["fishWinter"]["drops"],
                    "Winter",
                    spawner.location_name,
                )

            spawner.calculate_percent_chance()

            if report_progress is not None:
                report_progress()
            spawners.append(spawner)
        except:
            logging.error("Could not parse %s", path, exc_info=True)
    return spawners
