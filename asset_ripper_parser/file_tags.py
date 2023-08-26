"""Holds data relevant to organizing files by relevant in-game categories"""
from enum import Enum
import re


class FileTagLabel(Enum):
    """All labels used when tagging files for easier reference"""

    AMARI = "amari"
    ANGEL = "angel"
    ANIMAL = "animal"
    ARMOR = "armor"
    BOOK = "book"
    BULLETIN_BOARD = "bulletin board"
    CHARACTER_CUSTOMIZATION = "character customization"
    CLOTHING = "clothing"
    DECORATION = "decoration"
    DEMON = "demon"
    DUNGEON_CHEST = "dungeon chest"
    DUNGEON_FLOOR = "dungeon floor"
    ELF = "elf"
    ELEMENTAL = "elemental"
    ENEMY = "enemy"
    FISH_SPAWNER = "fish spawner"
    FISH_NET = "fish net"
    GIFT_TABLE = "gift table"
    ITEM = "item"
    NAGA = "naga"
    NPC = "npc"
    MINE = "mine"
    MERCHANT_TABLE = "merchant table"
    MUSEUM = "museum"
    PLACEABLE = "placeable"
    PROGRESS = "progress"
    QUEST = "quest"
    RECIPE = "recipe"
    RECIPE_LIST = "recipe list"
    SCENE = "scene"
    SEED = "seed"
    SKILL = "skill"
    SKILL_TREE = "skill tree"
    SKILL_TOME = "skill tome"
    STATTED = "statted"
    WALLPAPER = "wallpaper"


class FileTag:
    """Contains file category and how to determine whether file should be included in
    that category.
    """

    def __init__(
        self, label: FileTagLabel, filename_matcher=None, text_matcher=None
    ) -> None:
        self.label = label
        self.filename_matcher = filename_matcher
        self.text_matcher = text_matcher

    def check_filename(self, filename: str) -> bool:
        """Checks text against file matcher


        Args:
            filename (str): name of file to check

        Returns:
            bool: true if file should be given FileTagLabel
        """
        if self.filename_matcher is None:
            return True
        return self.filename_matcher(filename)

    def check_file_text(self, text: str) -> bool:
        """Checks contents of file and returns True if file tag is applicable.

        Args:
            text (str): file contents read as string.

        Returns:
            bool: True if file should be given FileTagLabel
        """
        if self.text_matcher is None:
            return True
        return self.text_matcher(text)


file_tags = [
    FileTag(FileTagLabel.ANGEL),
    FileTag(FileTagLabel.ANIMAL, text_matcher=lambda x: "animalName" in x),
    FileTag(FileTagLabel.AMARI),
    FileTag(FileTagLabel.ARMOR, text_matcher=lambda x: "armorMaterial: 1" in x),
    FileTag(FileTagLabel.BOOK, text_matcher=lambda x: "bookName" in x),
    FileTag(
        FileTagLabel.BULLETIN_BOARD,
        text_matcher=lambda x: "sunHavenBulletinBoardQuests" in x,
    ),
    FileTag(
        FileTagLabel.CHARACTER_CUSTOMIZATION,
        text_matcher=lambda x: "availableAtCharacterSelect" in x,
    ),
    FileTag(
        FileTagLabel.CLOTHING,
        filename_matcher=lambda x: re.match(r"[0-9]{3,5} - .+\.asset", x) is not None,
        text_matcher=lambda x: "clothingLayerData" in x,
    ),
    FileTag(FileTagLabel.DECORATION, text_matcher=lambda x: "placeableOnTables:" in x),
    FileTag(FileTagLabel.DEMON),
    FileTag(FileTagLabel.DUNGEON_CHEST, text_matcher=lambda x: "lockedText" in x),
    FileTag(FileTagLabel.DUNGEON_FLOOR, text_matcher=lambda x: "dungeonEntrance" in x),
    FileTag(FileTagLabel.ELEMENTAL),
    FileTag(FileTagLabel.ELF),
    FileTag(FileTagLabel.ENEMY, text_matcher=lambda x: "_hasAttack: 1" in x),
    FileTag(
        FileTagLabel.FISH_NET, text_matcher=lambda x: "fish:" in x and "large" in x
    ),
    FileTag(
        FileTagLabel.FISH_SPAWNER,
        text_matcher=lambda x: "fish:" in x and "large" not in x,
    ),
    FileTag(FileTagLabel.GIFT_TABLE, filename_matcher=lambda x: "GiftTable.asset" in x),
    FileTag(
        FileTagLabel.ITEM,
        filename_matcher=lambda x: re.match(r"[0-9]{3,5} - .+\.asset", x) is not None,
    ),
    FileTag(FileTagLabel.NAGA),
    FileTag(FileTagLabel.MINE, text_matcher=lambda x: "canDropRustyKey" in x),
    FileTag(FileTagLabel.MUSEUM, text_matcher=lambda x: "bundle" in x),
    FileTag(FileTagLabel.NPC, text_matcher=lambda x: "_oneLiners" in x),
    FileTag(
        FileTagLabel.MERCHANT_TABLE, filename_matcher=lambda x: "MerchantTable" in x
    ),
    FileTag(
        FileTagLabel.PLACEABLE,
        text_matcher=lambda x: "useAbleByPlayer: 1" in x
        and "_decoration:" in x
        and "_itemData:" in x,
    ),
    FileTag(FileTagLabel.PROGRESS, text_matcher=lambda x: "progressID" in x),
    FileTag(FileTagLabel.QUEST, text_matcher=lambda x: "questName" in x),
    FileTag(
        FileTagLabel.RECIPE,
        filename_matcher=lambda x: re.match(r"Recipe [0-9]+", x) is not None,
    ),
    FileTag(FileTagLabel.RECIPE_LIST, filename_matcher=lambda x: "RecipeList" in x),
    FileTag(FileTagLabel.SEED, filename_matcher=lambda x: " Seed" in x),
    FileTag(FileTagLabel.SKILL, text_matcher=lambda x: "nodePoints:" in x),
    FileTag(FileTagLabel.SKILL_TREE, filename_matcher=lambda x: "SkillTree.asset" in x),
    FileTag(FileTagLabel.SKILL_TOME, filename_matcher=lambda x:
        "Recipe " in x and "Skill Tome.asset" in x
    ),
    FileTag(FileTagLabel.STATTED, text_matcher=lambda x: "stats" in x),
    FileTag(FileTagLabel.SCENE, filename_matcher=lambda x: x.endswith(".unity")),
    FileTag(FileTagLabel.WALLPAPER, text_matcher=lambda x: "wallpaper:" in x),
]
