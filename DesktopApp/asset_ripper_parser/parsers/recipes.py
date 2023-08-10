import logging
import pprint
import re
from DesktopApp.asset_ripper_parser.exported_file_parser import parse_exported_file
from DesktopApp.asset_ripper_parser.index_files import FileIndexer
from DesktopApp.asset_ripper_parser.parsers.skill_progress import skill_progress_markers
from DesktopApp.asset_ripper_parser.utils import camel_case_split


class Ingredient:
    def __init__(self):
        self.name = ""
        self.amount = 1


class Recipe:
    def __init__(self):
        self.name = ""
        self.inputs: list[Ingredient] = []
        self.output: Ingredient = Ingredient()

        self.craft_time = 0

        self.workbench = None
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
        result.append(
            f"{ingredients_label:<15} = {';'.join([item.name + '*' + str(item.amount) for item in self.inputs])}"
        )

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
                sources.append(self.to_words(source.strip()))

        result.append(f"{recipesource_label:<15} = {';'.join(sources)}")

        result.append("}}")

        return "\n".join(result)


def parse_recipe(indexer, path):
    recipe = Recipe()
    recipe_name = re.search(r"Recipe [0-9]+ - (.+)\.asset", path)
    if recipe_name is not None:
        recipe.name = recipe_name.group(1)
    else:
        recipe.name = path

    components = parse_exported_file(path)
    main_component = components[0]["MonoBehaviour"]
    try:
        for input in main_component["input"]:
            ingredient = Ingredient()
            ingredient.name = indexer.find_name_from_guid(input["item"]["guid"])
            ingredient.amount = input["amount"]
            recipe.inputs.append(ingredient)

        recipe.output.name = indexer.find_name_from_guid(
            main_component["output"]["item"]["guid"]
        )
        recipe.output.amount = indexer.find_name_from_guid(
            main_component["output"]["amount"]
        )

        try:
            recipe.craft_time = float(main_component["hoursToCraft"])
        except ValueError:
            pass

        if isinstance(main_component["characterProgressTokens"], list):
            recipe.required_progress = [
                indexer.find_name_from_guid(x["guid"]).replace(".asset", "")
                for x in main_component["characterProgressTokens"]
            ]

        if isinstance(main_component["worldProgressTokens"], list):
            recipe.required_progress += [
                indexer.find_name_from_guid(x["guid"]).replace(".asset", "")
                for x in main_component["worldProgressTokens"]
            ]

        return recipe
    except:
        pprint.pprint(main_component)
        logging.error(f"Couldn't parse {recipe.name}", exc_info=True)


def parse_recipes(
    indexer: FileIndexer,
    recipe_lists_paths: list[str],
    # recipe_paths: list[str],
    report_progress=None,
) -> list[Recipe]:
    """
    Given a list of asset file paths, return a list of Recipe objects containing relevant data.
    """
    recipes = []
    for path in recipe_lists_paths:
        try:
            components = parse_exported_file(path)
            main_component = components[0]["MonoBehaviour"]
            list_paths = [
                indexer.find_filepath_from_guid(x["guid"])
                for x in main_component["craftingRecipes"]
            ]

            for recipe_path in list_paths:
                if recipe_path is not None:
                    recipe = parse_recipe(indexer, recipe_path)
                    recipe.workbench = (
                        path.split("\\")[-1]
                        .replace("RecipeList_", "")
                        .replace("RecipeList _", "")
                        .replace(".asset", "")
                    )
                    recipes.append(recipe)

                if report_progress is not None:
                    report_progress()
        except:
            logging.error("Couldn't parse %s", path, exc_info=True)

    return recipes
