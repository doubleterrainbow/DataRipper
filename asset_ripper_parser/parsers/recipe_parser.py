"""All methods related to parsing Recipes from asset file paths."""
import logging
import os
import pprint
import re
from asset_ripper_parser.models.skill_tome_recipe import SkillTomeRecipe
from asset_ripper_parser.parse_exported_file import parse_exported_file
from asset_ripper_parser.index_files import FileIndexer
from asset_ripper_parser.models.recipe import Ingredient, Recipe
from asset_ripper_parser.parse_serialized_data import SkillTomeParser


def parse_recipe(indexer: FileIndexer, main_component: dict) -> Recipe | None:
    """Parses a single recipe given a file path to an asset file.

    Args:
        indexer (FileIndexer): used for item lookups and lookups
        main_component (dict): object containing relevant recipe data

    Returns:
        Recipe: the resulting data in a Recipe object, or None if
                there was an error while parsing.
    """
    recipe = Recipe()

    try:
        recipe_name = re.search(r"Recipe [0-9]+ - (.+)", main_component["m_Name"])
        if recipe_name is not None:
            recipe.name = recipe_name.group(1)
        else:
            recipe.name = main_component["m_Name"]

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


def parse_skill_tomes(
    indexer: FileIndexer, recipe_paths: list[str], report_progress=None
) -> list[SkillTomeRecipe]:
    """
    Given a list of asset file paths, return a list of Recipe objects containing relevant data.
    File paths should be recipe lists, meaning they contain the "craftingRecipes" attribute. This
    allows us to provide a workbench name with each recipe output.

    Args:
        indexer (FileIndexer): used for file lookup from GUIDs
        recipe_paths (list[str]): each path refers to a skill tome recipe asset
        report_progress (function, optional): Runs every time a recipe list is parsed.
                                                Defaults to None.

    Returns:
        list[Recipe]: the recipes used in asset files, in Recipe objects.
    """
    recipes = []
    for path in recipe_paths:
        try:
            components = parse_exported_file(path)
            main_component = components[0]["MonoBehaviour"]

            skill_tome_recipe = SkillTomeRecipe(parse_recipe(indexer, main_component))
            skill_tome_recipe.workbench = "Anvil"

            serialized_parser = SkillTomeParser(
                main_component["serializationData"]["SerializedBytes"],
                lambda index, lookup_type: indexer.find_name_from_guid(
                    main_component["serializationData"]["ReferencedUnityObjects"][
                        index
                    ]["guid"]
                ),
            )
            skill_recipes = serialized_parser.parse()

            for random_recipe in skill_recipes:
                inner_recipe = Recipe()
                inner_recipe.output = skill_tome_recipe.output
                inner_recipe.craft_time = skill_tome_recipe.craft_time
                inner_recipe.workbench = skill_tome_recipe.workbench
                inner_recipe.required_progress = skill_tome_recipe.required_progress

                for ingredient in random_recipe:
                    inner_ingredient = Ingredient()
                    inner_ingredient.name = ingredient["item"]
                    inner_ingredient.amount = ingredient["amount"]
                    inner_recipe.inputs.append(inner_ingredient)
                skill_tome_recipe.recipes.append(inner_recipe)

            if report_progress is not None:
                report_progress()

            recipes.append(skill_tome_recipe)
        except:
            logging.error("Couldn't parse %s", path, exc_info=True)

    return recipes


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
                    main_component = parse_exported_file(recipe_path)[0][
                        "MonoBehaviour"
                    ]
                    recipe = parse_recipe(indexer, main_component)
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
