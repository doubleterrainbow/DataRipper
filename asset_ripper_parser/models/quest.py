from asset_ripper_parser.utils import camel_case_split


class Quest:
    def __init__(self):
        self.name = ""
        self.short_description = ""
        self.description = ""
        self.turn_in_text = ""
        self.turn_in_to_npc = ""
        self.days = 1
        self.repeatable = False
        self.progress_requirements = []
        self.requires = []
        self.rewards = []
        self.bonus_rewards = []

    def __str__(self) -> str:
        result = [f"{self.name} ({self.days} Days)"]
        result.append("Can repeat" if self.repeatable else "Does not repeat")
        if self.short_description is not None:
            result.append(f"{self.short_description}")
        result.append(f"{self.description}")
        result.append(f"Requirements: {', '.join(self.progress_requirements)}")
        result.append(f"Turn in to: {self.turn_in_to_npc}")
        result.append(f"Response: {self.turn_in_text}")

        return "\n".join(result)

    def to_wiki_tags(self) -> str:
        result = ["{{QUEST"]
        result.append(f"|name      = {self.name}")

        objective_items = []
        for item in self.requires:
            if item.amount > 1:
                objective_items.append(f"{item.amount} {item.name}s")
            else:
                objective_items.append(f"{item.name}")
        result.append(
            f"|objective = Bring {self.turn_in_to_npc} {' and '.join(objective_items)}."
        )
        result.append(
            "|link      = <!-- Only needed if page is a subpage of a different page -->"
        )
        result.append("|type      = character")
        result.append(
            f"|time      = {'Unlimited' if self.days == -1 else str(self.days) + ' Days'}"
        )
        result.append(f"|npc       = {self.turn_in_to_npc}")
        result.append("|location  = [[Sun Haven]]")

        progress_requirements = [
            camel_case_split(x) for x in self.progress_requirements
        ]
        result.append(f"|prereq    = {', '.join(progress_requirements)}")
        result.append("<!-- Quest Requirements and Rewards -->")

        requires = [f"{x.name}*{x.amount}" for x in self.requires]
        result.append("|requires = " + ";".join(requires))

        rewards = [f"{x.name}*{x.amount}" for x in self.rewards]
        result.append("|rewards   = " + ";".join(rewards))

        bonus_rewards = [f"{x.name}*{x.amount}" for x in self.bonus_rewards]
        result.append("|bonus     = " + ";".join(bonus_rewards))
        result.append("}}")

        result.append("==Overview==")
        result.append("{{Quest overview")

        result.append("|requires = " + ";".join(requires))
        result.append("|rewards = " + ";".join(rewards))
        result.append("|bonus = " + ";".join(bonus_rewards))

        result.append("}}")

        result.append("==Quest Complete Text==")
        result.append("Upon turning in this quest, the NPC will say:")
        result.append("{{" + f"Chat|{self.turn_in_to_npc}|{self.turn_in_text}" + "}}")

        return "\n".join(result)


class BulletinBoardQuest(Quest):
    def __init__(self):
        super().__init__()
        self.bulletin_board_description = ""

    def __str__(self) -> str:
        result = super().__str__()

        result += f"\n{self.bulletin_board_description}"
        return result
