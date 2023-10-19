"""Extra functionality used in several parsers"""
import re


def camel_case_split(text) -> str:
    """
    Splits a string on upper case characters.
    i.e. "MiningSkillTree" becomes "Mining Skill Tree"
    """
    camel_list = _camel_case_list(text)
    return " ".join(camel_list)


def camel_case_to_words(text) -> str:
    return re.sub(r"([A-Z0-9])", " \\1", text)


def _camel_case_list(text) -> list[str]:
    """
    Splits a string on upper case characters into a list.
    i.e. "MiningSkillTree" becomes ["Mining", "Skill", "Tree"]
    """
    previous_case = True  # case of previous char
    word = buffer = ""  # current word, buffer for last uppercase letter
    for character in text:
        upper = character.isupper()
        if previous_case and upper:
            word += buffer
            buffer = character
        elif previous_case and not upper:
            if len(word) > 0:
                yield word
            word = buffer + character
            buffer = ""
        elif not previous_case and upper:
            yield word
            word = ""
            buffer = character
        else:  # not previous_case and not upper:
            word += character
        previous_case = upper
    if len(word) > 0 or len(buffer) > 0:  # flush
        yield word + buffer


def clean_text(text):
    """Replace in-game markers with wiki markers. Notably, line breaks
    and player name.

    Args:
        text (str): dialogue from game.

    Returns:
        str: dialogue more usable on the wiki.
    """
    return (
        text.replace("XX", "{{PLAYER}}")
        .replace("[]", "<br>")
        .replace("<i>", "''")
        .replace("</i>", "''")
        .replace('\\"', '"')
    )


def get_stat_for_index(index: int) -> str:
    return camel_case_to_words(
        [
            "Health",
            "Mana",
            "AttackDamage",
            "AttackSpeed",
            "HealthRegen",
            "ManaRegen",
            "Movespeed",
            "Jump",
            "SpellDamage",
            "MeleeLifesteal",
            "RangedLifeSteal",
            "MovespeedOnHit",
            "MovespeedOnKill",
            "HealthOnKill",
            "Crit",
            "DamageReduction",
            "GoldGain",
            "Knockback",
            "StunDuration",
            "Size",
            "FishingSkill",
            "MiningSkill",
            "ExplorationSkill",
            "Defense",
            "FlatDamage",
            "RomanceBonus",
            "MoneyPerDay",
            "BonusCombatEXP",
            "BonusWoodcuttingEXP",
            "BonusFishingEXP",
            "BonusMiningEXP",
            "BonusCraftingEXP",
            "BonusFarmingEXP",
            "StunChance",
            "Accuracy",
            "FarmingSkill",
            "GoldPerCraft",
            "MiningCrit",
            "WoodcuttingCrit",
            "SmithingSkill",
            "BonusExperience",
            "SpellPower",
            "SwordPower",
            "CrossbowPower",
            "CritDamage",
            "Dodge",
            "FreeAirSkipChance",
            "FishingMinigameSpeed",
            "FishBobberAttraction",
            "EnemyGoldDrop",
            "ExtraForageableChance",
            "BonusTreeDamage",
            "MiningDamage",
            "FallDamageReduction",
            "MovementSpeedAfterRock",
            "FruitManaRestore",
            "SpellAttackSpeed",
            "Power",
            "WoodcuttingDamage",
            "CommunityTokenPerDay",
            "TicketsPerDay",
            "TripleGoldChance",
            "PickupRange",
            "ExtraCropChance",
            "FishingWinArea",
            "FishingSweetSpotArea",
            "ManaPerCraft",
            "BlackGemDropChance",
            "CraftingSpeed",
            "MiningDamageWithergate",
            "OrbsPerDay",
        ][index]
    )


def get_stat_amount_for_index(index: int):
    if index == 0:
        return "very small"
    elif index == 1:
        return "small"
    elif index == 2:
        return "moderate"
    elif index == 3:
        return "large"
    elif index == 4:
        return "huge"
    return ""
