import math
import pprint


class MemoryLossPotionResponse:
    def __init__(self):
        self.npc_name = ""
        self.initial_response = ""
        self.married_response = ""
        self.platonic_response = ""

    def __str__(self) -> str:
        return (
            "{{Memory Loss Dialogue|"
            + f"{self.npc_name}|Collapse=True"
            + f"\n|Dialogue     = {self.initial_response}\n|PotionAction ="
            + f"\n|PostDialogue = {self.married_response}\n|PostPlatonic = {self.platonic_response}\n"
            + "}}"
        )
