import logging

from asset_ripper_parser.index_files import FileIndexer
from asset_ripper_parser.models.barn_animal import BarnAnimal
from asset_ripper_parser.models.random_drop import RandomDrop
from asset_ripper_parser.models.recipe import Ingredient
from asset_ripper_parser.parse_exported_file import parse_exported_file


def parse_drops(indexer: FileIndexer, drops: list) -> list[list[RandomDrop]]:
    """
    Given a list of drops from an asset, returns a dict containing
    the drop chance, amount, and name of item being dropped.

    Args:
        indexer (FileIndexer): used to look up the item names.
        drops (list[dict]): given a relevant asset, reads the '_drops' property

    Returns:
        list[list[RandomDrop]]: a minimal and readable list of drops.
    """
    result = []
    for drop_group in drops:
        individual_drops = []
        for drop in drop_group["drops"]:
            if "guid" not in drop["drop"]:
                name = None
            else:
                name = indexer.find_name_from_guid(drop["drop"]["guid"])

            individual_drops.append(
                RandomDrop(
                    item_name=name,
                    drop_weight=drop["dropChance"],
                    min_amount=drop["dropAmount"]["x"],
                    max_amount=drop["dropAmount"]["y"],
                    percent_chance=0,
                )
            )

        result.append(individual_drops)

    return result


def parse_barn_animals(
    indexer: FileIndexer, filepaths: list[str], report_progress=None
):
    """Given a list of file paths, returns a list of Mail objects.

    Each file is opened and read for relevant data.

    Args:
        indexer (FileIndexer): used for file lookups
        filepaths (list[str]): file paths like <RNPC_NAME>GiftTable.asset
        report_progress (function, optional): Runs every time a gift table is parsed.
                                            Defaults to None.

    Returns:
        list[BarnAnimal]: parsed GiftTable objects containing data relevant to a RNPC
    """
    animals = []
    for path in filepaths:
        animal = BarnAnimal()
        try:
            components = parse_exported_file(path)
            main_component = [
                x
                for x in components
                if "MonoBehaviour" in x and "goldenDrop" in x["MonoBehaviour"]
            ][0]["MonoBehaviour"]

            animal.animal_name = main_component["animalName"]
            animal.capacity = main_component["animalCapacity"]

            if (
                "itemToDrop" in main_component
                and "guid" in main_component["itemToDrop"]
            ):
                animal.drop = Ingredient(
                    name=indexer.find_name_from_guid(
                        main_component["itemToDrop"]["guid"]
                    ),
                    amount=main_component["amountToDrop"],
                )

            if (
                "goldenDrop" in main_component
                and "guid" in main_component["goldenDrop"]
            ):
                animal.golden_drop = indexer.find_name_from_guid(
                    main_component["goldenDrop"]["guid"]
                )

            if main_component["_drops"]:
                animal.random_drops = parse_drops(indexer, main_component["_drops"])
                animal.calculate_drop_percents()

            animals.append(animal)

            if report_progress is not None:
                report_progress(f"Completed {animal.animal_name}")
        except:
            logging.error("Couldn't parse %s", path, exc_info=True)

    return animals
