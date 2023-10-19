from asset_ripper_parser.models.random_drop import RandomDrop
from asset_ripper_parser.models.recipe import Ingredient


class BarnAnimal:
    def __init__(self):
        self.animal_name = ""
        self.drop: Ingredient = None
        self.golden_drop: str = None
        self.capacity = 1
        self.random_drops: list[list[RandomDrop]] = []

    def calculate_drop_percents(self):
        """Calculates the percent chance for any item to drop."""
        if not self.random_drops:
            return

        for group in self.random_drops:
            total_weight = sum(drop.drop_weight for drop in group)

            for drop in group:
                drop.percent_chance = (drop.drop_weight / total_weight) * 100

    def __str__(self) -> str:
        result = [self.animal_name, f"|capacity = {self.capacity}"]

        if self.drop is not None:
            result.append(f"|produce = {self.drop.name} * {self.drop.amount}")

        if self.golden_drop is not None:
            result.append(f"|goldenProduce = {self.golden_drop}")

        if self.random_drops:
            for drop in self.random_drops:
                for dropped_item in drop:
                    if dropped_item.item_name != "":
                        amount = str(dropped_item.min_amount)
                        if dropped_item.min_amount != dropped_item.max_amount:
                            amount += f"-{dropped_item.max_amount}"

                        result.append(
                            f"\t{amount} {dropped_item.item_name} "
                            + f"({round(dropped_item.percent_chance, 2)}%)"
                        )

        return "\n".join(result)

    # def to_wiki_tags(self) -> str:
    #     result = ["{{Mail|Collapse=False", f"|{self.heart_level}", f"|{self.message}"]
    #
    #     if self.gifts:
    #         gift_tags = "|"
    #         for gift in self.gifts:
    #             gift_tags += "{{i|" + f"{gift.name}|x={gift.amount}" + "}}"
    #         result.append(gift_tags)
    #
    #     result.append("}}")
    #     return "\n".join(result)
