import math
import pprint


class CutsceneDialogue:
    def __init__(self):
        self.npc = None
        self.options = []
        self.responses = []


class Cutscene:
    def __init__(self, name: str):
        self.name = name
        self.dialogues = []

    def __str__(self) -> str:
        result = [self.name]

        for dialogue in self.dialogues:
            result.append(pprint.pformat(dialogue, indent=4))

        return "\n".join(result)

    def _format_manual_table(self):
        result = ['{| class="tablemedium"']

        small_space = "width:15%; "
        small_after_prefix = "width:85%; "

        med_space = "width:30%; "

        align_top = "|- valign=top"
        npc_face = "|style=\"SPACEtext-align:right; border-top:0px; border-right:0px;\" | '''{{il|NPC|nl|size=25px|img=Face NPC}}''':"
        npc_prefix = '|style="SPACEborder-top:0px; border-left:0px;" colspan=3|'

        player_header = "|style=\"width:15%; text-align:right; border-top:0px; border-right:0px; color:#69ac52;\" | '''Player''':"
        player_text = '|style="width:85%; border-top:0px; border-left:0px;" colspan=3| {{IfDesktop|TEXT|<small>&nbsp;TEXT</small>}}'

        index = 0
        while index < len(self.dialogues):
            dialogue_text = self.dialogues[index]["text"]
            options = self.dialogues[index]["options"]

            result.append(align_top)

            if dialogue_text != "":
                result.append(
                    f"{npc_face.replace('SPACE', small_space).replace('NPC', self.dialogues[index]['npc'])}"
                )
                result.append(
                    f"{npc_prefix.replace('SPACE', small_after_prefix)}{dialogue_text}"
                )

            for option in options:
                heart = ""
                if option["hearts"] != 0:
                    heart = (
                        " {{Heart Points"
                        + f"|{'-' if option['hearts'] < 0 else '+'}|{abs(option['hearts'])}"
                        + "}}"
                    )

                result.append(align_top)
                result.append(player_header)
                result.append(f"{player_text.replace('TEXT', option['text'])}")

                if "response" in option:
                    index += 1
                    response = self.dialogues[index]
                    result.append(align_top)
                    result.append(
                        f"{npc_face.replace('SPACE', med_space).replace('NPC', self.dialogues[index]['npc'])}"
                    )
                    result.append(
                        f"{npc_prefix.replace('SPACE', '')}{response['text']}"
                    )

                    inner_options = self.dialogues[index]["options"]
                    for option2 in inner_options:
                        heart = ""
                        if option["hearts"] != 0:
                            heart = (
                                " {{Heart Points"
                                + f"|{'-' if option['hearts'] < 0 else '+'}|{abs(option['hearts'])}"
                                + "}}"
                            )

                        result.append(align_top)
                        result.append(player_header)
                        result.append(f"{player_text.replace('TEXT', option2['text'])}")

            index += 1

        result.append("|}")
        return result

    def to_wiki_tags(self, template="Event Scene"):
        result = []
        if template == "Event Scene":
            result = ["{{Event Scene/header|" + self.name + "|Collapse=True}}"]

            indent = " "
            index = 0
            while index < len(self.dialogues):
                dialogue_text = self.dialogues[index]["text"]
                options = self.dialogues[index]["options"]

                if dialogue_text != "":
                    result.append(
                        "{{"
                        + f"Event Scene|indent={indent}|{self.dialogues[index]['npc']}|{dialogue_text}"
                        + "}}"
                    )

                if len(options) > 1:
                    indent = "1"
                else:
                    indent = " "

                for option in options:
                    heart = ""
                    if option["hearts"] != 0:
                        heart = (
                            " {{Heart Points"
                            + f"|{'-' if option['hearts'] < 0 else '+'}|{abs(option['hearts'])}"
                            + "}}"
                        )

                    result.append(
                        "{{"
                        + f"Event Scene|indent={indent}|Player|{option['text']}{heart}"
                        + "}}"
                    )

                    if "response" in option:
                        index += 1
                        response = self.dialogues[index]
                        result.append(
                            "{{"
                            + f"Event Scene|indent=2|{response['npc']}|{response['text']}"
                            + "}}"
                        )

                        inner_options = self.dialogues[index]["options"]
                        for option2 in inner_options:
                            heart = ""
                            if option["hearts"] != 0:
                                heart = (
                                    " {{Heart Points"
                                    + f"|{'-' if option['hearts'] < 0 else '+'}|{abs(option['hearts'])}"
                                    + "}}"
                                )

                            result.append(
                                "{{"
                                + f"Event Scene|indent={indent}|Player|{option2['text']}{heart}"
                                + "}}"
                            )

                index += 1
            result.append("{{Event Scene/footer}}")
        elif template == "Table":
            result = self._format_manual_table()

        return "\n".join(result)
