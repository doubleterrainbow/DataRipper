"""Contains functionality to convert assets to Monsters"""
import logging
import pprint
from asset_ripper_parser.exported_file_parser import parse_exported_file
from asset_ripper_parser.index_files import FileIndexer
from asset_ripper_parser.models.monster import Monster


def parse_drops(indexer: FileIndexer, drops: list) -> list[dict]:
    """
    Given a list of drops from an asset, returns a dict containing
    the drop chance, amount, and name of item being dropped.

    Each drop will look like:
    ```
    {
        "item": "name of the item",
        "chance": 5, # the weight of dropping this item
        "amount_x": 1, # the minimum amount of the item that will drop
        "amount_y": 3, # the maximum amount of the item that will drop
        "percent_chance": 0 # initialized at 0, this is utilized by calculate_drop_percents()
    }
    ```

    Args:
        indexer (FileIndexer): used to look up the item names.
        drops (list[dict]): given a relevant asset, reads the '_drops' property

    Returns:
        list[dict]: a minimal and readable list of drops.
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
                {
                    "item": name,
                    "chance": drop["dropChance"],
                    "amount_x": drop["dropAmount"]["x"],
                    "amount_y": drop["dropAmount"]["y"],
                    "percent_chance": 0,
                }
            )

        result.append(individual_drops)

    return result


def parse_monsters(
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
    monsters = []
    for path in filepaths:
        monster = Monster()
        try:
            components = parse_exported_file(path)

            main_component = [
                comp
                for comp in components
                if "MonoBehaviour" in comp and "enemyName" in comp["MonoBehaviour"]
            ]
            damage_component = [
                comp
                for comp in components
                if "MonoBehaviour" in comp and "_damageRange" in comp["MonoBehaviour"]
            ]
            try:
                monster_data = main_component[0]["MonoBehaviour"]

                monster.name = monster_data["enemyName"]
                monster.spawner_id = monster_data["enemySpawnerName"]
                monster.health = monster_data["_health"]
                monster.experience = monster_data["_experience"]
                monster.level = monster_data["_powerLevel"]
                monster.defense = monster_data["defense"]

                if damage_component:
                    monster.min_damage = damage_component[0]["MonoBehaviour"][
                        "_damageRange"
                    ]["x"]
                    monster.max_damage = damage_component[0]["MonoBehaviour"][
                        "_damageRange"
                    ]["y"]
                else:
                    logging.debug("Couldn't find damage for %s", monster.name)

                monster.drops = parse_drops(indexer, monster_data["_drops"])
                monster.calculate_drop_percents()

                monsters.append(monster)
            except:
                pprint.pprint(components)
                logging.error("Could not parse %s", path, exc_info=True)

            if report_progress is not None:
                report_progress()
        except:
            logging.error("Couldn't parse %s", path, exc_info=True)

    return monsters
