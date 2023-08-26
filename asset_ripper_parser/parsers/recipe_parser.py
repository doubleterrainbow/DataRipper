"""All methods related to parsing Recipes from asset file paths."""
import logging
import os
import pprint
import re
from asset_ripper_parser.exported_file_parser import parse_exported_file
from asset_ripper_parser.index_files import FileIndexer
from asset_ripper_parser.models.recipe import Ingredient, Recipe


def parse_recipe(indexer: FileIndexer, path: str) -> Recipe:
    """Parses a single recipe given a file path to an asset file.

    Args:
        indexer (FileIndexer): used for item lookups and lookups
        path (str): full path to the asset file we are interested in

    Returns:
        Recipe: the resulting data in a Recipe object, or None if
                there was an error while parsing.
    """
    recipe = Recipe()
    recipe_name = re.search(r"Recipe [0-9]+ - (.+)\.asset", path)
    if recipe_name is not None:
        recipe.name = recipe_name.group(1)
    else:
        recipe.name = path

    components = parse_exported_file(path)
    main_component = components[0]["MonoBehaviour"]
    try:
        for recipe_input in main_component["input"]:
            ingredient = Ingredient()
            ingredient.name = indexer.find_name_from_guid(recipe_input["item"]["guid"])
            ingredient.amount = recipe_input["amount"]
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
        logging.error("Couldn't parse %s", recipe.name, exc_info=True)
        return None


def parse_recipes(
    indexer: FileIndexer,
    recipe_lists_paths: list[str],
    report_progress=None,
) -> list[Recipe]:
    """
    Given a list of asset file paths, return a list of Recipe objects containing relevant data.
    File paths should be recipe lists, meaning they contain the "craftingRecipes" attribute. This
    allows us to provide a workbench name with each recipe output.

    Args:
        indexer (FileIndexer): used for file lookup from GUIDs
        recipe_lists_paths (list[str]): each path refers to a recipe list asset file
        report_progress (function, optional): Runs every time a recipe list is parsed.
                                              Defaults to None.

    Returns:
        list[Recipe]: the recipes used in asset files, in Recipe objects.
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
                    if recipe is not None:
                        recipe.workbench = (
                            os.path.basename(path)
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
