import enum

from asset_ripper_parser.parse_sprite_sheet import Sprite

clothing_colors = {
    10: "Red",
    20: "Brown",
    30: "Orange",
    40: "Hazel",
    50: "Yellow",
    60: "Green",
    70: "Blue",
    80: "Darkblue",
    90: "Purple",
    100: "Darkpink",
    110: "Pink",
    120: "Lightpink",
    200: "White",
    210: "Gray",
    220: "Black",
    510: "SkinTone1",
    520: "SkinTone2",
    530: "SkinTone3",
    540: "SkinTone4",
    550: "SkinTone5",
    560: "SkinTone6",
    570: "SkinTone7",
    580: "SkinTone8",
    590: "SkinTone9",
    600: "SkinTone10",
    610: "SkinTone11",
    620: "SkinTone12",
}


class ClothingDirection(enum.Enum):
    LEFT = 0
    RIGHT = 1
    FRONT = 2
    BACK = 3


class ClothingType(enum.Enum):
    Cape = "cape"
    Dress = "dress"
    Hat = "hat"
    Pants = "pant"
    Shirt = "chest"
    Skirt = "skirt"
    Gloves = "gloves"


class Clothing:
    def __init__(self, name="", color=""):
        self.base_name = name
        self.color = color
        self.clothing_type = ClothingType.Hat
        self.icon = Sprite()
        self.sprite = Sprite()
        self.sleeves_sprite = Sprite()

    def to_list(self) -> list:
        result = [self.base_name, self.color, self.clothing_type.value]

        result += [
            self.icon.x,
            self.icon.y,
            self.icon.width,
            self.icon.height,
            self.icon.image_path,
        ]

        result += [
            self.sprite.x,
            self.sprite.y,
            self.sprite.width,
            self.sprite.height,
            self.sprite.image_path,
        ]

        result += [
            self.sleeves_sprite.x,
            self.sleeves_sprite.y,
            self.sleeves_sprite.width,
            self.sleeves_sprite.height,
            self.sleeves_sprite.image_path,
        ]

        return result
