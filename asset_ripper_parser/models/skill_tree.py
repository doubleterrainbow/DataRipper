"""Contains all classes that store information about in-game skills"""

from asset_ripper_parser.parse_sprite_sheet import Sprite


class Skill:
    """Stores data relevant to a skill in-game"""

    def __init__(self):
        self.name = ""
        self.title = ""
        self.description = ""
        self.points = 1
        self.sprite = Sprite()

    def __str__(self):
        result = []

        result.append(f"{self.title} ({self.name})")
        result.append(f"\t{self.description}")
        result.append(f"\t{str(self.sprite)}")

        return "\n".join(result)


class SkillTree:
    """Stores data relevant to a skill tree in-game"""

    def __init__(self):
        self.name = ""
        self.skills: list[Skill] = []

    def __str__(self):
        return self.name + "\n" + "\n\n".join([str(skill) for skill in self.skills])
