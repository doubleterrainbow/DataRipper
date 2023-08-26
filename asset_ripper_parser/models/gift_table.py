"""Contains classes relevant to gifting items to RNPCs"""
from difflib import SequenceMatcher
from enum import Enum
import itertools


class GiftLevel(Enum):
    """Represents how good a gift is."""

    LOVE = "love"
    LIKE = "like"
    NEUTRAL = "good"
    DISLIKE = "dislike"
    UNIQUE = "unique"


class UniqueGiftResponse:
    """Represents a gift response not attached to the goodness of the item."""

    def __init__(self, item_name, response):
        self.item_name = item_name
        self.response = response


class GiftsAndResponse:
    """Holds dialogue(s) for gifting an item and
    which items produce that response.

    The data defines list of responses, but all instances only contain one response.
    We are using a list in case this changes in the future, and to align with the
    data structure in the asset.
    """

    def __init__(self, level: GiftLevel) -> None:
        self.gift_level = level
        self.responses = []
        self.items = []
        self.birthday_reponse = ""

    def __str__(self) -> str:
        result = []
        result.append(f"|{self.gift_level.value}Response = {', '.join(self.responses)}")
        result.append(f"|{self.gift_level.value} = {', '.join(self.items)}")

        if self.gift_level != GiftLevel.NEUTRAL:
            category_label = (
                self.gift_level.value[0].upper() + self.gift_level.value[1:]
            )
            result.append(
                f"|{self.gift_level.value}Groups = "
                + f"[[:Category:Universally_{category_label}d_Gifts|"
                + f"Universally {category_label}d Items]]"
            )

        return "\n".join(result)


class GiftTable:
    """For any NPC, this gift table holds the golden key for which
    gifts to give if you want them to love you, and which to give
    if you want them to hate you.
    """

    def __init__(self) -> None:
        self.npc_name = ""

        self.loved = GiftsAndResponse(GiftLevel.LOVE)
        self.liked = GiftsAndResponse(GiftLevel.LIKE)
        self.neutral = GiftsAndResponse(GiftLevel.NEUTRAL)
        self.disliked = GiftsAndResponse(GiftLevel.UNIQUE)

        self.unique_items = []

    def __str__(self):
        result = [self.npc_name]
        result.append("{{NPC Gift Preferences")

        result.append(str(self.loved))
        result.append(str(self.liked))
        result.append(str(self.neutral))
        result.append(str(self.disliked))

        result.append("}}")

        grouped_unique_gifts = itertools.groupby(
            self.unique_items, lambda x: x.response
        )
        for key, group in grouped_unique_gifts:
            names = [x.item_name for x in group]
            if len(names) > 3:
                match = SequenceMatcher(None, names[0], names[1]).find_longest_match()
                common_words = names[0][match.a : match.a + match.size]
                if len(common_words.strip()) > 1 and common_words.strip()[0].isupper():
                    name = "Any " + names[0][match.a : match.a + match.size].strip()
                else:
                    name = ", ".join(names)
            else:
                name = ", ".join(names)
            result.append(f"{name}: {key}")

        return "\n".join(result)
