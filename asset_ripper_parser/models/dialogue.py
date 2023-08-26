class DialogueLine:
    def __init__(self) -> None:
        self.dialogue = ""
        self.options: list[str] = []
        self.responses = []


class Dialogue:
    def __init__(self, npc, cycle=0, one_liner=False) -> None:
        self.npc = npc
        self.cycle = cycle
        self.one_liner = one_liner
        self.lines: list[DialogueLine] = []
