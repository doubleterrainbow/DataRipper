import pprint


class FishDrop:
    def __init__(self) -> None:
        self.item = None
        self.season = "All"
        self.location = "Farm"
        self.chance = 0
        self.min_percent_chance = 0
        self.max_percent_chance = 0

    def __str__(self):
        return (
            "{{Fishing spawn"
            + (
                f"|{self.season}|{self.location}|{round(self.min_percent_chance, 2)}%"
                f"|{round(self.max_percent_chance, 2)}%"
            )
            + "}}"
        )


class FishSpawn:
    def __init__(self) -> None:
        self.location_name = ""
        self.drops = []
        self.spring_drops = []
        self.summer_drops = []
        self.fall_drops = []
        self.winter_drops = []

    @staticmethod
    def _lerp(a: float, b: float, t: float) -> float:
        """Linear interpolate on the scale given by a to b, using t as the point on that scale.
        Examples
        --------
            50 == lerp(0, 100, 0.5)
            4.2 == lerp(1, 5, 0.8)
        """
        return (1 - t) * a + t * b

    def _adjusted_odds_based_on_rarity_and_level(self, rarity, level):
        if rarity == 2:
            return self._lerp(0.8, 3.35, level / 120)
        elif rarity == 3:
            return self._lerp(0.675, 4.25, level / 120)
        elif rarity == 4:
            return self._lerp(0.55, 5, level / 120)
        else:
            return 1

    def _calculate_percentages(
        self, drops, level, familiar_waters_value=0.0, advanced_fish_mapping_value=0.0
    ):
        num = 0.0
        num2 = 0.0
        if familiar_waters_value:
            num += 0.05 * familiar_waters_value
        if advanced_fish_mapping_value:
            num2 += 0.1 * advanced_fish_mapping_value

        total_probability = 0.0
        for fish_loot in drops:
            num3 = 1.0
            fish_rarity = fish_loot.item.rarity
            if fish_rarity == 3:  # Epic
                num3 += num
            elif fish_rarity == 4:  # Legendary
                num3 += num + num2

            adjusted_odds = self._adjusted_odds_based_on_rarity_and_level(
                fish_rarity, level
            )
            total_probability += fish_loot.chance * num3 * adjusted_odds

        result = []
        for fish_loot in drops:
            rarity_adjustment = 1.0
            fish_rarity = fish_loot.item.rarity
            if fish_rarity == 3:  # Epic
                rarity_adjustment += num
            elif fish_rarity == 4:  # Legendary
                rarity_adjustment += num + num2

            adjusted_odds = self._adjusted_odds_based_on_rarity_and_level(
                fish_rarity, level
            )
            num5 = fish_loot.chance * rarity_adjustment * adjusted_odds

            percent_chance = (num5 / total_probability) * 100
            result.append({"name": fish_loot.item.name, "percent": percent_chance})

        return result

    def _calculate_drop_chances(self, drops: list[FishDrop]):
        min_chances = self._calculate_percentages(drops, level=1)
        max_chances = self._calculate_percentages(
            drops,
            level=70,
            familiar_waters_value=15,
            advanced_fish_mapping_value=30,
        )

        for drop in drops:
            min_chance = [x for x in min_chances if x["name"] == drop.item.name]
            max_chance = [x for x in max_chances if x["name"] == drop.item.name]
            drop.min_percent_chance = min_chance[0]["percent"]
            drop.max_percent_chance = max_chance[0]["percent"]

        return drops

    def calculate_percent_chance(self):
        self.drops = self._calculate_drop_chances(self.drops)
        self.spring_drops = self._calculate_drop_chances(self.spring_drops)
        self.summer_drops = self._calculate_drop_chances(self.summer_drops)
        self.fall_drops = self._calculate_drop_chances(self.fall_drops)
        self.winter_drops = self._calculate_drop_chances(self.winter_drops)

    def __str__(self):
        result = [self.location_name]
        result += [str(x) for x in self.drops]
        result += [str(x) for x in self.spring_drops]
        result += [str(x) for x in self.summer_drops]
        result += [str(x) for x in self.fall_drops]
        result += [str(x) for x in self.winter_drops]

        return "\n".join(result)
