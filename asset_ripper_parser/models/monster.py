"""All classes related to enemies in the game."""
from asset_ripper_parser.models.random_drop import RandomDrop


class Monster:
    """Describes stats of an enemy."""

    def __init__(self) -> None:
        self.name = ""
        self.spawner_id = ""
        self.health = 0
        self.experience = 0
        self.level = 0
        self.defense = 0
        self.min_damage = 0
        self.max_damage = 0
        self.ranged = False

        self.drops: list[list[RandomDrop]] = []

    def __str__(self):
        result = [
            self.name + f" (level {self.level})",
            f"Spawner: {self.spawner_id}",
            f"Health: {self.health}",
            f"Experience: {self.experience}",
            f"Defense: {self.defense}",
            f"Damage: {self.min_damage}-{self.max_damage}",
        ]

        for drop in self.drops:
            for dropped_item in drop:
                if dropped_item.item_name is not None:
                    amount = str(dropped_item.min_amount)
                    if dropped_item.min_amount != dropped_item.max_amount:
                        amount += f"-{dropped_item.max_amount}"

                    result.append(
                        f"\t{amount} {dropped_item.item_name} "
                        + f"({round(dropped_item.percent_chance, 2)}%)"
                    )

        return "\n".join(result)

    def calculate_drop_percents(self):
        """Calculates the percent chance for any item to drop."""
        if not self.drops:
            return

        for group in self.drops:
            total_weight = sum(drop.drop_weight for drop in group)

            for drop in group:
                drop.percent_chance = (drop.drop_weight / total_weight) * 100
