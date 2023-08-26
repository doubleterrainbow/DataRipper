"""Contains the class for Furniture objects"""
from asset_ripper_parser.models.item import Item


class Furniture(Item):
    """Represents an item that can be placed by the player."""

    def __init__(self):
        super().__init__("")
        self.type = "Misc"
        self.placed_on = "floor"
        self.rotatable = False
        self.is_dlc = False

    def __str__(self):
        sprite_text = ""
        if self.sprite.name != "":
            sprite_text = str(self.sprite)

        return (
            f"{self.name} ({self.item_id}) | {self.type} | {self.placed_on} | "
            + f"rotates={self.rotatable} | {self.sells_for} {self.sell_type} | {sprite_text}"
        )

    def to_wiki_template(self):
        """Creates a string representation of this object
        for use on the wiki in a {{Furniture summary}} template

        Returns:
            str: {{Furniture summary}} template with populated values.
        """
        return (
            "{{"
            + f"Furniture summary|{self.type}|"
            + f"placement={self.placed_on}|rotate="
            + "yes"
            if self.rotatable
            else "no" + "|set=" + "}}"
        )

    def determine_type(self):
        """Assigns a type to this object
        based on its name and placement. Defaults to "Misc"
        """
        all_categories = [
            "Bed",
            "Bookcase",
            "Chair",
            "Chest",
            "Couch",
            "Counter",
            "Fence",
            "Fireplace",
            "Instrument",
            "Lighting",
            "Nightstand",
            "Painting",
            "Pet Items",
            "Plant",
            "Plushie",
            "Refrigerator",
            "Rug",
            "Selling Portal",
            "Shelf",
            "Stove",
            "Table",
            "TV",
            "Wardrobe",
            "Bridge",
            "Mailbox",
            "Tile",
            "Wallpaper",
            "Window",
        ]

        lighting_names = ["Lamp"]
        bookshelf_names = ["Bookshelf", "Bookcase"]
        table_names = ["Table", "Desk"]
        plush_names = ["Plush", "Plushie"]
        chair_names = ["Seat", "Chair"]

        is_light = [
            light_name for light_name in lighting_names if light_name in self.name
        ]
        is_bookcase = [
            bookcase_name
            for bookcase_name in bookshelf_names
            if bookcase_name in self.name
        ]
        is_table = [table_name for table_name in table_names if table_name in self.name]
        is_plush = [plush_name for plush_name in plush_names if plush_name in self.name]
        is_chair = [chair_name for chair_name in chair_names if chair_name in self.name]

        self.type = "Misc"
        relevant_type = []
        if is_light or self.name.endswith("Light"):
            self.type = "Lighting"
        elif is_bookcase:
            self.type = "Bookcase"
        elif is_table:
            self.type = "Table"
        elif is_plush:
            self.type = "Plushie"
        elif is_chair:
            self.type = "Chair"
        else:
            relevant_type = [
                furn_type for furn_type in all_categories if furn_type in self.name
            ]
            if relevant_type:
                self.type = relevant_type[0]
