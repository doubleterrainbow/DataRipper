"""Contains classes relevant to gifting items to RNPCs"""
from difflib import SequenceMatcher
from enum import Enum
import itertools

from asset_ripper_parser.utils import clean_text


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
        self.birthday_response = ""

    def __str__(self) -> str:
        result = [
            f"|{self.gift_level.value}Response = {', '.join([clean_text(x) for x in self.responses])}",
            f"|{self.gift_level.value} = {', '.join(self.items)}",
        ]

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
        self.disliked = GiftsAndResponse(GiftLevel.DISLIKE)

        self.unique_items = []

    def __str__(self):
        result = [
            "{{NPC Gift Preferences",
            str(self.loved),
            str(self.liked),
            str(self.neutral),
            str(self.disliked),
            "}}",
            "===Birthday Responses===",
            "If the player gives {{BASEPAGENAME}} a gift on their [[Calendar|birthday]], they will get one of these "
            "generic responses based on the level of the gift. {{BASEPAGENAME}}'s birthday is the "
            "REPLACE_WITH_BIRTHDAY",
        ]

        for b_day_response in [
            x.birthday_response
            for x in [self.loved, self.liked, self.disliked, self.neutral]
        ]:
            result.append("{{chat||" + clean_text(b_day_response) + "}}")

        result.append("\n===Unique===")
        result.append("{{BASEPAGENAME}} has several unique lines for gifts.<br><br>")

        grouped_unique_gifts = itertools.groupby(
            self.unique_items, lambda x: x.response
        )
        for key, group in grouped_unique_gifts:
            names = [x.item_name for x in group]
            # if len(names) > 3:
            #     match = SequenceMatcher(None, names[0], names[1]).find_longest_match()
            #     common_words = names[0][match.a : match.a + match.size]
            #     if len(common_words.strip()) > 1 and common_words.strip()[0].isupper():
            #         name = "any " + names[0][match.a : match.a + match.size].strip()
            #     else:
            #         name = ", ".join(names)
            # else:
            #     name = ", ".join(names)

            name_links = " or ".join(
                ", ".join([f"[[{x}]]" for x in names]).rsplit(", ", maxsplit=1)
            )
            result.append(f"When gifted {name_links}:")
            result.append("{{chat||" + clean_text(key) + "}}")

        return "\n".join(result)