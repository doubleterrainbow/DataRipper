"""Functionality for reading scene files and outputting what enemies spawn there."""
import logging
import os
from asset_ripper_parser.parse_exported_file import parse_exported_file
from asset_ripper_parser.models.location import Location, MonsterSpawn
from asset_ripper_parser.utils import camel_case_split


def get_monster_names(monster_paths: list[str]) -> dict:
    """
    Creates a dictionary mapping spawners to monster names

    Args:
        monster_paths (list[str]): file paths of enemies containing spawner names

    Returns:
        dict: Map of enemy spawner ID to enemy name
    """
    monster_names = {}
    for monster_path in monster_paths:
        parsed_monster = parse_exported_file(monster_path)
        main_component = [
            comp
            for comp in parsed_monster
            if "MonoBehaviour" in comp and "enemyName" in comp["MonoBehaviour"]
        ]
        monster_data = main_component[0]["MonoBehaviour"]
        name = monster_data["enemyName"]
        spawner_id = monster_data["enemySpawnerName"]

        if spawner_id is not None:
            monster_names[spawner_id] = name
    return monster_names


def parse_monster_spawns(
    paths: list[str],
    monster_paths: list[str],
    report_progress=None,
) -> list[Location]:
    """Given a list of file paths, returns a list of locations.

    Args:
        paths (list[str]): all ".unity" files
        monster_paths (list[str]): monster asset files for looking up name from spawner
        report_progress (function, optional):   Called when an location has been parsed.
                                                Defaults to None.

    Returns:
        list[Location]: List of parsed locations.
    """
    spawns = []
    monster_names = get_monster_names(monster_paths)
    for path in paths:
        try:
            scene_components = parse_exported_file(path, only_with_text="enemy")

            spawnable_components = [
                x
                for x in scene_components
                if "MonoBehaviour" in x and "enemy" in x["MonoBehaviour"]
            ]
            if spawnable_components:
                location = Location()
                location.name = camel_case_split(
                    os.path.basename(path).replace(".unity", "")
                )

                enemies = []
                for spawn_component in spawnable_components:
                    spawn = MonsterSpawn()
                    spawn.spawner_name = spawn_component["MonoBehaviour"]["enemy"]

                    if spawn.spawner_name in monster_names:
                        spawn.monster_name = monster_names[spawn.spawner_name]

                    spawn.spawn_chance = spawn_component["MonoBehaviour"]["spawnChance"]

                    enemies.append(spawn)
                location.monster_spawns = enemies

                spawns.append(location)

            if report_progress is not None:
                report_progress()
        except:
            logging.error("Could not parse %s", path, exc_info=True)
    return spawns
