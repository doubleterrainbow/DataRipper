"""Contains a class that holds information about items in the game."""
import re
from asset_ripper_parser.parse_sprite_sheet import Sprite
from asset_ripper_parser.utils import get_stat_for_index, get_stat_amount_for_index


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

        self.restores_health = 0
        self.restores_mana = 0
        self.food_stat_increase = 0
        self.food_stat = -1

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

    def to_wiki_tags(self) -> str:
        """
        {{Item infobox
            |name        = Item name (default is PAGENAME)
            |image       = Image name.png (default is PAGENAME.png)
            |description = Description (default uses the description template and PAGENAME)

            <!-- Common Information -->
            |sell        = Sell price (numberic).
            |selltype    = Currency this item is sold in.
            |stack       = Maximum numer of that items can be placed in a single stack (numeric).
            |rarity      = Rarity (numeric).
            |hearts      = Base gift level (numeric).

            <!-- Item Classification -->
            |itemType    =
            |subtype     =
            |category    =
            |dlc         = If true, this will add the "DLC" category to the page. Leave blank if false.

            <!-- Item Data-->
            |restores    = How much health and mana this item restores to the user. (Use stats template. Put ";" between multiple items)
            |statInc     = Which stat this item will permanently increase upon consumption. (Plain text ONLY!)
            |statAmt     = How much the stat will be permanently increased upon consumption. (Plain text ONLY!)

            |region      = Region of this item. (Sun Haven / Withergate / Nel'Vari)
            |source      = What type of thing this comes from. (Node Name, Tree Name, etc)
            |season      = Which season(s) this item is available (spring, summer, fall, winter, any)
            |seed        = Seed the crop comes from. (DO NOT USE A LINK. Plain text ONLY!)
            |produces    = What that item produces. (Plain text ONLY! Put ";" between multiple items)
            |exp         = How much exp this gives the player (numeric).
            |requirement = Required level to equip: {{SkillLevel|SKILLNAME|#}}
            |armorset    = Armor Set on the /Armor page [[:Armor#SET_NAME|DISPLAY_NAME]]
            |oraganic    = If this item is impacted by the skill "Organic" put this as "1". If not, leave blank.
            }}
        """
        result = []

        result.append(f"|name = {self.name}")
        result.append(f"|sell = {self.sells_for}")
        result.append(f"|selltype = {self.sell_type}")
        result.append(f"|stack = {self.stack_size}")
        result.append(f"|rarity = {self.rarity}")
        result.append(f"|hearts = {self.hearts}")

        if self.is_dlc:
            result.append(f"|dlc = {self.is_dlc}")

        if self.restores_health or self.restores_mana:
            restores = []
            if self.restores_health:
                restores.append("{{Stats|Health|+ " + str(self.restores_health) + "}}")
            if self.restores_mana:
                restores.append("{{Stats|Mana|+ " + str(self.restores_mana) + "}}")
            result.append("|restores = " + ";".join(restores))

        if self.food_stat >= 0:
            result.append("|statInc  = " + get_stat_for_index(self.food_stat))
            result.append(
                "|statAmt = " + get_stat_amount_for_index(self.food_stat_increase)
            )

        return "\n".join(result)
