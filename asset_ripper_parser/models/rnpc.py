from enum import IntEnum
from math import floor

from asset_ripper_parser.models.dialogue import add_heart_points, apply_tags
from asset_ripper_parser.models.gift_table import GiftTable
from asset_ripper_parser.models.mail import Mail
from asset_ripper_parser.models.season import Season


class RelationshipLevel(IntEnum):
    STRANGERS = 0
    FRIENDS = 1
    DATING = 2
    MARRIAGE = 3


class OneLiner:
    def __init__(self):
        self.text = ""
        self.season = Season.ANY
        self.level = RelationshipLevel.STRANGERS

    def to_wiki_tags(self, name=""):
        tagged_text = apply_tags(self.text, name)
        season = (
            " {{il|" + self.season.name.capitalize() + " Token|icon|size=20px}}"
            if self.season != Season.ANY
            else ""
        )
        return "{{chat||" + f"{tagged_text}{season}" + "}}"


class Dialogue:
    def __init__(self):
        self.text = ""
        self.number = 0
        self.sub_letter = None
        self.is_response = False
        self.add_relationship = 0


class DialogueCycle:
    def __init__(self):
        self.number = 0
        self.level = RelationshipLevel.STRANGERS
        self.dialogue = []

    def to_wiki_tags(self, name=""):
        """
        ==== Cycle 5====
        {{Conversation Dialogue|Claude
        |Cycle 5
        |Dialogue=... Hm? Oh - pardon me, {{PLAYER}}. I was in another world, thinking about music.
        |Option1=You still haven't told me much about your music.
        |Option2=Do you ever share your music?
        |Response1=I don't know what to tell you. I make it, it comes out wrong, I make it again.
        |Response2=I don't share my music with anybody.
        |Option1a=Nothing great ever happened on the first try. <span style="color: #3cb043;">'''+2 {{il|Heart|icon|size=14px}} Points'''</span>
        |Option1b=Maybe you should just move on to another project. <span style="color: #dc2626;">'''-1 {{il|Heart|icon|size=14px}} Points'''</span>
        |Response1a=There's truth to that, even if it's kind of an annoying truth. I'll try to remember that, {{PLAYER}}.
        |Response1b=Thanks {{PLAYER}}, but I don't need you to tell me how to give up. I already know how to do that.
        |Option2a=Wouldn't it be helpful to have other people listen to it?
        |Option2b=If you ever want an outside opinion on your work, I'm happy to help.
        |Response2a=It's about meeting my own standards, {{PLAYER}}. What do I care what other people think?
        |Response2b=I guess you're probably my first choice at this point. I don't want to get your hopes up, though.
        }}
        """
        content = ""
        for line in self.dialogue:
            tagged_text = apply_tags(line.text, name)

            if line.number == 0:
                content += f"|Dialogue = {tagged_text}\n"
            else:
                prefix = "Response" if line.is_response else "Option"
                letter = line.sub_letter if line.sub_letter is not None else ""
                content += f"|{prefix}{line.number}{letter} = {tagged_text}\n"

        title = f"Cycle {self.number}"
        if self.level == RelationshipLevel.FRIENDS:
            title = f"Cycle P{self.number}"
        return (
            f"\n===={title}===="
            + "\n{{Conversation Dialogue|{{BASEPAGENAME}}"
            + f"\n|{title}\n"
            + content
            + "}}"
        )


class WalkPath:
    def __init__(self, name, hour):
        self.name = name
        self.hour = hour

    def __eq__(self, other):
        if not isinstance(other, WalkPath):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.name == other.name and self.hour == other.hour


class WalkCycle:
    def __init__(self):
        self.path_name = "Default"
        self.paths = []

    def has_same_paths(self, paths: list[WalkPath]):
        return self.paths == paths


class MarriedGift:
    def __init__(self, name, dialogue, amount):
        self.dialogue = dialogue
        self.item_name = name
        self.amount = amount


class RNPC:
    def __init__(self, name):
        self.name = name
        self.one_liners = []
        self.dialogues = []
        self.gifting_lines = []
        self.gift_table = GiftTable()
        self.walk_cycles = []
        self.mail: list[Mail] = []
        self.married_gifts: list[MarriedGift] = []

    def one_liners_to_wiki_tags(self):
        result = [
            "==General Dialogue==",
            "If there is a seasonal token at the end of the dialogue, it means the player can only see that "
            "dialogue during that season.",
            "\n===Strangers===",
        ]
        for line in self.one_liners:
            if line.level == RelationshipLevel.STRANGERS:
                result.append(line.to_wiki_tags(name=self.name))

        result.append("\n===Friends===")
        for line in self.one_liners:
            if line.level == RelationshipLevel.FRIENDS:
                result.append(line.to_wiki_tags(name=self.name))

        result.append("\n===Dating===")
        for line in self.one_liners:
            if line.level == RelationshipLevel.DATING:
                result.append(line.to_wiki_tags(name=self.name))

        result.append("\n===Married===")
        for line in self.one_liners:
            if line.level == RelationshipLevel.MARRIAGE:
                result.append(line.to_wiki_tags(name=self.name))

        return "\n".join(result)

    def dialogue_cycles_to_wiki_tags(self):
        result = [
            "==Conversations==",
            "===Strangers===",
        ]
        for line in self.dialogues:
            if line.level == RelationshipLevel.STRANGERS:
                result.append(line.to_wiki_tags(name=self.name))

        if [x for x in self.dialogues if x.level == RelationshipLevel.FRIENDS]:
            result.append("===Friends===")
            for line in self.dialogues:
                if line.level == RelationshipLevel.FRIENDS:
                    result.append(line.to_wiki_tags(name=self.name))

        if [x for x in self.dialogues if x.level == RelationshipLevel.DATING]:
            result.append("===Dating===")
            for line in self.dialogues:
                if line.level == RelationshipLevel.DATING:
                    result.append(line.to_wiki_tags(name=self.name))

        if [x for x in self.dialogues if x.level == RelationshipLevel.MARRIAGE]:
            result.append("===Married===")
            for line in self.dialogues:
                if line.level == RelationshipLevel.MARRIAGE:
                    result.append(line.to_wiki_tags(name=self.name))

        return "\n".join(result)

    def walk_cycles_to_wiki_tags(self):
        """
        {{Schedule |character = Anne
        |1_name    = General
        |1_1_time  = 6:00
        |1_1_info  = Gets out of bed.
        |1_2_time  = 7:30
        |1_2_info  = Walks to the general store.
        |1_3_time  = 10:00
        |1_3_info  = Shuffles around the general store.
        |1_4_time  = 11:30
        |2_name    = Married
        |2_1_time  = 6:00
        |2_1_info  = Gets out of bed in the Player's house.
        |2_2_time  = 6:30
        |2_2_info  = Leaves the Player's House.
        |2_3_time  = 7:30
        }}
        """
        unique_cycles = []
        for cycle in self.walk_cycles:
            same_path_cycles = [
                x for x in unique_cycles if x.has_same_paths(cycle.paths)
            ]
            if not same_path_cycles:
                unique_cycles.append(cycle)

        result = [
            "==Schedule==",
            f"{self.name} has {len(unique_cycles)} schedules that they follow. [[{self.name}'s House]] is "
            f"available to the player 8AM - 8PM.",
            "{{Schedule |character = " + self.name,
        ]

        written_cycles = []
        for i in range(0, len(unique_cycles)):
            cycle = unique_cycles[i]

            name = cycle.path_name.replace("_", "")

            if name in written_cycles:
                continue
            written_cycles.append(name)
            result.append(f"|{i + 1}_name    = {name}")

            for walk_action_index in range(0, len(cycle.paths)):
                path = cycle.paths[walk_action_index]
                humanized_hour = floor(path.hour)

                hour_remainder = path.hour - floor(path.hour)
                minutes = ":00"
                if hour_remainder == 0.5:
                    minutes = ":30"
                elif hour_remainder != 0:
                    minutes = f".{hour_remainder}"
                result.append(
                    f"|{i + 1}_{walk_action_index + 1}_time    = {humanized_hour}{minutes}"
                )

                walk_path_name = path.name if path.name is not None else "Unknown"
                humanized_name = (
                    walk_path_name.replace("go to", "Walks to")
                    .replace("start in", "Wakes up in")
                    .replace("quest board", "Bulletin Board")
                )
                result.append(
                    f"|{i + 1}_{walk_action_index + 1}_info    = {humanized_name}."
                )

        result.append("}}")
        return "\n".join(result)

    def married_gifts_to_wiki_tags(self):
        result = [
            "===Morning Gifts===",
            f"When married to {self.name}, there is a chance he will have a gift for the player. This is indicated by "
            f"a quest marker above his head, and will be available until the player talks to him.\n",
        ]

        for gift in self.married_gifts:
            gifting_text = "When gifting {{il|" + gift.item_name
            if gift.amount > 1:
                gifting_text += f"|x={gift.amount}"
            gifting_text += "}}:"
            result.append(gifting_text)
            result.append("{{chat||" + gift.dialogue + "}}")

        return "\n".join(result)
