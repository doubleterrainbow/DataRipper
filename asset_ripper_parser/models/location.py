"""Stores data about a location, usually referring to a unity scene."""


class MonsterSpawn:
    """A chance that an enemy will appear."""

    def __init__(self) -> None:
        self.spawner_name = ""
        self.monster_name = None
        self.spawn_chance = 100

    def __str__(self) -> str:
        name = self.monster_name if self.monster_name is not None else self.spawner_name
        if self.spawn_chance != 100:
            return f"{name.strip()} ({round(self.spawn_chance * 100)}%)"
        return name.strip()


class Location:
    """Information relevant to a scene in the game. A "scene" refers to a unity scene file."""

    def __init__(self):
        self.name = ""
        self.monster_spawns = []

    def __str__(self) -> str:
        result = [self.name]

        grouped_spawns = {}
        for monster in self.monster_spawns:
            if str(monster) not in grouped_spawns:
                grouped_spawns[str(monster)] = 1
            else:
                grouped_spawns[str(monster)] += 1

        for key, value in grouped_spawns.items():
            result.append(f"\tx{value} {key}")

        return "\n".join(result)
