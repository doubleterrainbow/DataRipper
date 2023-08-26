"""All classes related to enemies in the game."""


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

        self.drops = []

    def __str__(self):
        result = [self.name + f" (level {self.level})"]

        result.append(f"Spawner: {self.spawner_id}")
        result.append(f"Health: {self.health}")
        result.append(f"Experience: {self.experience}")
        result.append(f"Defense: {self.defense}")
        result.append(f"Damage: {self.min_damage}-{self.max_damage}")

        for drop in self.drops:
            for dropped_item in drop:
                if dropped_item["item"] is not None:
                    amount = str(dropped_item["amount_x"])
                    if dropped_item["amount_x"] != dropped_item["amount_y"]:
                        amount += f"-{dropped_item['amount_y']}"

                    result.append(
                        f"\t{amount} {dropped_item['item']} "
                        + f"({round(dropped_item['percent_chance'], 2)}%)"
                    )

        return "\n".join(result)

    def calculate_drop_percents(self):
        """Calculates the percent chance for any item to drop."""
        if not self.drops:
            return

        for group in self.drops:
            total_weight = sum(drop["chance"] for drop in group)

            for drop in group:
                drop["percent_chance"] = (drop["chance"] / total_weight) * 100
