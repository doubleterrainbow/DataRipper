"""All functionality to convert furniture asset filepaths into Furniture objects"""
import logging
from DesktopApp.asset_ripper_parser.exported_file_parser import parse_exported_file
from DesktopApp.asset_ripper_parser.index_files import FileIndexer
from DesktopApp.asset_ripper_parser.parse_sprite_sheet import Sprite


class Furniture:
    def __init__(self):
        self.name = ""
        self.id = 0
        self.stack_size = 1
        self.category = "Misc"
        self.placed_on = "floor"
        self.sells_for = 0
        self.sell_type = "Coins"
        self.rarity = 0
        self.hearts = 1
        self.rotatable = False
        self.is_dlc = False
        self.sprite = Sprite()

    def __str__(self):
        sprite_text = ""
        if self.sprite.name != "":
            sprite_text = str(self.sprite)

        return f"{self.name} ({self.id}) | {self.category} | {self.placed_on} | rotates={self.rotatable} | {self.sells_for} {self.sell_type} | {sprite_text}"

    def to_wiki_template(self):
        """Creates a string representation of this object 
        for use on the wiki in a {{Furniture summary}} template

        Returns:
            str: {{Furniture summary}} template with populated values.
        """
        return "{{" + f"Furniture summary|{self.category}|placement={self.placed_on}|rotate={'yes' if self.rotatable else 'no'}|set=" + "}}"
    
    def determine_category(self):
        """Assigns a category to this object
        based on its name and placement. Defaults to "Misc"
        """
        all_categories = [   
            'Bed', 'Bookcase',
            'Chair', 'Chest', 'Couch', 'Counter', 'Fence', 'Fireplace',
            'Instrument', 'Lighting', 'Nightstand', 
            'Painting', 'Pet Items', 'Plant', 'Plushie', 'Refrigerator', 'Rug', 'Selling Portal',
            'Shelf', 'Stove', 'Table', 'TV', 'Wardrobe', 'Bridge', 'Mailbox', 'Tile', 'Wallpaper',
            'Window',
        ]

        lighting_names = ["Lamp"]
        bookshelf_names = ["Bookshelf", "Bookcase"]
        table_names = ["Table", "Desk"]
        plush_names = ["Plush", "Plushie"]
        chair_names = ["Seat", "Chair"]

        is_light = [light_name for light_name in lighting_names if light_name in self.name]
        is_bookcase = [bookcase_name for bookcase_name in bookshelf_names if bookcase_name in self.name]
        is_table = [table_name for table_name in table_names if table_name in self.name]
        is_plush = [plush_name for plush_name in plush_names if plush_name in self.name]
        is_chair = [chair_name for chair_name in chair_names if chair_name in self.name]

        self.category = "Misc"
        relevant_category = []
        if is_light or self.name.endswith("Light"):
            self.category = "Lighting"
        elif is_bookcase:
            self.category = "Bookcase"
        elif is_table:
            self.category = "Table"
        elif is_plush:
            self.category = "Plushie"
        elif is_chair:
            self.category = "Chair"
        else:
            relevant_category = [furn_category for furn_category in all_categories
                                 if furn_category in self.name]
            if relevant_category:
                self.category = relevant_category[0]


def parse_decoration_data(
    indexer: FileIndexer,
    data_component: dict,
    furniture: Furniture) -> Furniture:
    """
    Given a MonoBehaviour dict from a furniture asset file, find 
    the decoration file and parse its data. That data is applied to
    the given Furniture object and returned. Namely, this is used 
    to determine where the item can be placed (floor, wall, or tables).
    
        Parameters:
            indexer (FileIndexer): used to lookup files
            data_component (dict): contains _decoration keyword to lookup the file
            furniture (Furniture): existing furniture item that needs decoration information added.
            
        Returns:
            furniture (Furniture): original Furniture with correct placed_on value.
    """
    try:
        decoration_filepath = indexer.find_filepath_from_guid(
            data_component["_decoration"]["guid"]
        )

        if decoration_filepath is not None:
            decoration = parse_exported_file(decoration_filepath)
            matching_decorations = [
                comp for comp in decoration if 'MonoBehaviour' in comp and \
                    "placeableOnTables" in comp['MonoBehaviour']
            ]
            decoration_component = matching_decorations[0]['MonoBehaviour']

            if decoration_component["placeableOnTables"] != 0:
                furniture.placed_on = "surface"
            elif decoration_component["placeableOnWalls"] != 0:
                furniture.placed_on = "wall"
            else:
                furniture.placed_on = "floor"

            if decoration_component["placeableAsRug"] != 0:
                furniture.category = "Rug"
    except:
        logging.error("Could not parse decoration %s", data_component['_decoration'], exc_info=True)

    return furniture

def parse_item_data(indexer: FileIndexer, data_component: dict, furniture: Furniture) -> Furniture:
    """Given a dict from a placeable asset, grabs the corresponding
    item reference and applies relevant data to furniture. Returns 
    the original furniture with item data applied. The data that's parsed
    here is namely the name, id, rarity, hearts, and sell price.

    Args:
        indexer (FileIndexer): used to lookup files based on GUID
        data_component (dict): dict from a placeable asset's 
                                MonoBehaviour section. Contains "_itemData".
        furniture (Furniture): furniture that needs item data associated with it.

    Returns:
        Furniture: original furniture from parameter but modified to include item data.
    """
    item_filepath = indexer.find_filepath_from_guid(
        data_component["_itemData"]["guid"]
    )

    if item_filepath is not None:
        item_component = parse_exported_file(item_filepath)[0]['MonoBehaviour']

        furniture.name = item_component["name"].strip()
        furniture.id = item_component["id"]
        furniture.stack_size = item_component["stackSize"]
        furniture.hearts = item_component["hearts"]
        furniture.rarity = item_component["rarity"]
        furniture.is_dlc = item_component["isDLCItem"] == 1

        if item_component["sellPrice"] > 0:
            furniture.sells_for = item_component["sellPrice"]
            furniture.sell_type = "Coins"
        elif item_component["orbsSellPrice"] > 0:
            furniture.sells_for = item_component["orbsSellPrice"]
            furniture.sell_type = "Orbs"
        elif item_component["ticketSellPrice"] > 0:
            furniture.sells_for = item_component["ticketSellPrice"]
            furniture.sell_type = "Tickets"

    return furniture


def parse_furniture(
    indexer: FileIndexer,
    placeables: list[str],
    report_progress = None
) -> list[Furniture]:
    """Given a list of Furniture asset file paths, creates a list 
    of Furniture objects.

    Args:
        indexer (FileIndexer): used for file lookups
        placeables (list[str]): list of file paths, each a prefab that is usable by the player.
        report_progress (function, optional): Run every time a Furniture object is parsed. 
                                              Defaults to None.

    Returns:
        list[Furniture]: All items that were found and able to be parsed from placeables.
    """
    furnitures = []
    for path in placeables:
        furniture = Furniture()
        parsed_furniture = parse_exported_file(path)
        main_component = [comp for comp in parsed_furniture\
            if "MonoBehaviour" in comp and \
                "_decoration" in comp["MonoBehaviour"] and "_itemData" in comp["MonoBehaviour"]
                ]

        data_component = main_component[0]['MonoBehaviour']

        furniture.rotatable = "_previewSprites" in data_component and \
            len(data_component["_previewSprites"]) > 0

        # pprint.pprint(data_component)
        furniture = parse_decoration_data(indexer, data_component, furniture)

        try:
            furniture = parse_item_data(indexer, data_component, furniture)
        except:
            logging.error(f"Could not parse item for %s", path, exc_info=True)
            game_object = [comp for comp in parsed_furniture if 'GameObject' in comp]
            furniture.name = game_object[0]['GameObject']['m_Name'].replace("_placeable", "")

        furniture.determine_category()

        if report_progress is not None:
            report_progress()

        furnitures.append(furniture)
    return furnitures
