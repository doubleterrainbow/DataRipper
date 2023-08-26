"""Contains classes used to represent information about craftables in game."""

from asset_ripper_parser.utils import camel_case_split
from asset_ripper_parser.parsers.skill_progress import skill_progress_markers


class Ingredient:
    """Defines an item name and the amount needed to craft."""

    def __init__(self):
        self.name = ""
        self.amount = 1


class Recipe:
    """Defines a recipe and the requirements for crafting it."""

    def __init__(self):
        self.name = ""
        self.inputs: list[Ingredient] = []
        self.output: Ingredient = Ingredient()

        self.craft_time = 0

        self.workbench = None

        # this is anything needed to obtain the recipe.
        # such as Mining Level 30 for crafting Sunite Bars
        self.required_progress = []

    def __str__(self):
        result = []

        result.append(f"{self.name}")

        result.append("{{Recipe")

        workbench_label = "|workbench"
        if self.workbench is None:
            workbench_name = ""
        else:
            workbench_name = (
                camel_case_split(self.workbench.strip())
                if " " not in self.workbench.strip()
                else self.workbench.strip()
            )
        result.append(f"{workbench_label:<15} = {workbench_name}")

        ingredients_label = "|ingredients"
        ingredients = [item.name + "*" + str(item.amount) for item in self.inputs]
        result.append(f"{ingredients_label:<15} = {';'.join(ingredients)}")

        time_label = "|time"
        crafting_time = str(self.craft_time)

        remainder_time = self.craft_time - int(self.craft_time)
        if remainder_time > 0:
            crafting_time = str(int(self.craft_time)) + "hr"
            if remainder_time == 0.25:
                crafting_time += " 15min"
            elif remainder_time == 0.33:
                crafting_time += " 20min"
            elif remainder_time == 0.5:
                crafting_time += " 30min"
            elif remainder_time == 0.66:
                crafting_time += " 40min"
            elif remainder_time == 0.75:
                crafting_time += " 45min"
        else:
            crafting_time = str(int(self.craft_time)) + "hr"

        crafting_time = crafting_time.replace("0hr", "").strip()
        result.append(f"{time_label:<15} = {crafting_time}")

        yield_label = "|yield"
        try:
            yield_result = (
                str(self.output.amount) if float(self.output.amount) > 1 else ""
            )
        except:
            yield_result = ""
        result.append(f"{yield_label:<15} = {yield_result}")

        recipesource_label = "|recipesource"
        sources = []
        for source in self.required_progress:
            if source in skill_progress_markers:
                sources.append(skill_progress_markers[source])
            else:
                sources.append(camel_case_split(source.strip()))

        result.append(f"{recipesource_label:<15} = {';'.join(sources)}")

        result.append("}}")

        return "\n".join(result)
