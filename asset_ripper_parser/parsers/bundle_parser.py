"""Contains functionality to convert assets to Monsters"""
import logging
import os.path
import pprint

from asset_ripper_parser.models.bundle import Bundle, BundleType
from asset_ripper_parser.models.item import Item
from asset_ripper_parser.models.recipe import Ingredient
from asset_ripper_parser.parse_exported_file import parse_exported_file
from asset_ripper_parser.index_files import FileIndexer
from asset_ripper_parser.models.monster import Monster
from asset_ripper_parser.parsers.item_parser import parse_item
from asset_ripper_parser.utils import camel_case_split


def parse_bundles(
    indexer: FileIndexer, filepaths: list[str], report_progress=None
) -> list[Monster]:
    """Given a list of asset file paths, returns a list of Monsters with relevant information.

    Args:
        indexer (FileIndexer): used for file lookups
        filepaths (list[str]): list of asset file paths containing enemy information
        report_progress (function, optional): Called every time a monster is parsed.
                                              Defaults to None.

    Returns:
        list[Monster]: Monster objects that can be used to create human-friendly outputs.
    """
    bundles = []
    for path in filepaths:
        bundle = Bundle()
        try:
            components = parse_exported_file(path)

            main_component = [
                comp
                for comp in components
                if "MonoBehaviour" in comp and "bundleType" in comp["MonoBehaviour"]
            ]
            bundle_component = main_component[0]["MonoBehaviour"]

            try:
                filename = os.path.basename(path)
                bundle.name = filename.replace(".prefab", "")
                bundle.bundle_type = BundleType(
                    bundle_component["bundleType"]
                ).name.lower()

                for reward in bundle_component["rewards"]:
                    item = Item("")
                    item_path = indexer.find_filepath_from_guid(reward["item"]["guid"])
                    item_component = parse_exported_file(item_path)[0]["MonoBehaviour"]
                    item.name = item_component["name"]
                    parsed_item = parse_item(indexer, item_component, item)

                    ing = Ingredient()
                    ing.name = parsed_item.name
                    ing.amount = reward["amount"]
                    bundle.rewards.append(ing)

                podium_components = [
                    comp
                    for comp in components
                    if "MonoBehaviour" in comp and "podiums" in comp["MonoBehaviour"]
                ]
                if podium_components:
                    podium_component = podium_components[0]["MonoBehaviour"]
                    podium_ids = [x["fileID"] for x in podium_component["podiums"]]
                    for component in components:
                        if component["file_id"] in podium_ids:
                            try:
                                if "guid" not in component["MonoBehaviour"]["itemData"]:
                                    ing = Ingredient()
                                    ing.name = "Unknown"
                                    ing.amount = 1
                                else:
                                    item_guid = component["MonoBehaviour"]["itemData"][
                                        "guid"
                                    ]
                                    filepath = indexer.find_filepath_from_guid(
                                        item_guid
                                    )
                                    item_component = parse_exported_file(filepath)[0][
                                        "MonoBehaviour"
                                    ]
                                    item = Item(item_component["name"])
                                    parsed_item = parse_item(
                                        indexer, item_component, item
                                    )
                                    ing = Ingredient()
                                    ing.name = parsed_item.name
                                    ing.amount = 1
                                bundle.inputs.append(ing)
                            except:
                                # pprint.pprint(component)
                                logging.error(
                                    "Error when getting %s bundle input %d",
                                    bundle.name,
                                    component["file_id"],
                                    exc_info=True,
                                )
                else:
                    # Attempt to use itemToAccept
                    try:
                        item_components = [
                            comp
                            for comp in components
                            if "MonoBehaviour" in comp
                            and "itemToAccept" in comp["MonoBehaviour"]
                        ]
                        item_data = [
                            x["MonoBehaviour"]
                            for x in item_components
                            if "guid" in x["MonoBehaviour"]["itemToAccept"]
                        ]
                        for data in item_data:
                            filepath = indexer.find_filepath_from_guid(
                                data["itemToAccept"]["guid"]
                            )
                            item_component = parse_exported_file(filepath)[0][
                                "MonoBehaviour"
                            ]
                            item = Item(item_component["name"])
                            parsed_item = parse_item(indexer, item_component, item)
                            ing = Ingredient()
                            ing.name = parsed_item.name
                            ing.amount = data["numberOfItemToAccept"]
                            bundle.inputs.append(ing)
                    except:
                        # pprint.pprint(components)
                        logging.error("Couldn't use itemToAccept", exc_info=True)

                bundles.append(bundle)
            except:
                # pprint.pprint(components)
                logging.error("Could not parse %s", path, exc_info=True)

            if report_progress is not None:
                report_progress()
        except:
            logging.error("Couldn't parse %s", path, exc_info=True)

    return bundles
