"""Contains classes used to represent information about craftables in game."""

from asset_ripper_parser.models.recipe import Ingredient, Recipe


class SkillTomeRecipe(Recipe):
    """Defines a skill tome recipe and the requirements for crafting it."""

    def __init__(self, recipe: Recipe):
        super().__init__()
        self.name = recipe.name
        self.inputs = recipe.inputs
        self.output = recipe.output
        self.craft_time = recipe.craft_time
        self.required_progress = recipe.required_progress
        self.workbench = recipe.workbench
        self.recipes: list[Recipe] = []

    def __str__(self):
        result = [f"{self.name}"]

        for recipe in self.recipes:
            result.append(str(recipe) + "\n")

        return "\n".join(result)
