"""Contains a class that holds information about items in the game."""
from DesktopApp.asset_ripper_parser.parse_sprite_sheet import Sprite


class Item:
    """Represents an item that can be placed into the player's inventory."""

    def __init__(self):
        self.name = ""
        self.item_id = 0
        self.stack_size = 1
        self.sells_for = 0
        self.sell_type = "Coins"
        self.rarity = 0
        self.hearts = 1
        self.sprite = Sprite()
