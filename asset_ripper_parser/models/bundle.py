from enum import IntEnum


class BundleType(IntEnum):
    SNACCOON = 0
    DYNUS_ALTAR = 1
    SLIME = 2
    MUSEUM_BUNDLE = 3


class Bundle:
    def __init__(self):
        self.name = ""
        self.bundle_type = "Unknown"
        self.season = None
        self.inputs = []
        self.rewards = []

    def __str__(self):
        inputs = [f"{x.amount}*{x.name}" for x in self.inputs]
        rewards = [f"{x.amount}*{x.name}" for x in self.rewards]
        return f"{self.name} ({self.bundle_type})\nRequires = {';'.join(inputs)}\nRewards = {';'.join(rewards)}"
