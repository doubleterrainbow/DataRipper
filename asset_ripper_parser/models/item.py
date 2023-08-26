"""Contains a class that holds information about items in the game."""
import re
from asset_ripper_parser.parse_sprite_sheet import Sprite


class Item:
    """Represents an item that can be placed into the player's inventory."""

    def __init__(self, name: str):
        self.name = re.sub(r"\([\w\s]+\)", "", name).strip()
        if "(" in name:
            self.variant = re.search(r"\(([\w\s]+)\)", name).group(1)
        else:
            self.variant = None

        self.item_id = 0
        self.description = ""
        self.stack_size = 1
        self.sells_for = 0
        self.sell_type = "Coins"
        self.rarity = 0
        self.hearts = 1
        self.is_dlc = False
        self.sprite = Sprite()

    def __str__(self):
        name = (
            f"{self.name} ({self.variant})" if self.variant is not None else self.name
        )

        sprite = ""
        if self.sprite.name != "":
            sprite = " | " + str(self.sprite)

        return (
            f"{name} ({self.item_id}) | sells for {self.sells_for} {self.sell_type} "
            + f"| rarity = {self.rarity} | hearts = {self.hearts}{sprite}"
        )
