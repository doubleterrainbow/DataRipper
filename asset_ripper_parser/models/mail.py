from asset_ripper_parser.models.item import Item
from asset_ripper_parser.models.recipe import Ingredient


class Mail:
    def __init__(self):
        self.npc_name = ""
        self.message = ""
        self.heart_level = 0
        self.gifts: list[Ingredient] = []
        self.progress: list[str] = []

    def to_wiki_tags(self) -> str:
        result = ["{{Mail|Collapse=False", f"|{self.heart_level}", f"|{self.message}"]

        if self.gifts:
            gift_tags = "|"
            for gift in self.gifts:
                gift_tags += "{{i|" + f"{gift.name}|x={gift.amount}" + "}}"
            result.append(gift_tags)

        result.append("}}")
        return "\n".join(result)
