def camel_case_split(text) -> str:
    """
    Splits a string on upper case characters.
    i.e. "MiningSkillTree" becomes "Mining Skill Tree"
    """
    camel_list = _camel_case_list(text)
    return " ".join(camel_list)


def _camel_case_list(text) -> list[str]:
    """
    Splits a string on upper case characters into a list.
    i.e. "MiningSkillTree" becomes ["Mining", "Skill", "Tree"]
    """
    previous_case = True  # case of previous char
    word = buffer = ""  # current word, buffer for last uppercase letter
    for character in text:
        upper = character.isupper()
        if previous_case and upper:
            word += buffer
            buffer = character
        elif previous_case and not upper:
            if len(word) > 0:
                yield word
            word = buffer + character
            buffer = ""
        elif not previous_case and upper:
            yield word
            word = ""
            buffer = character
        else:  # not previous_case and not upper:
            word += character
        previous_case = upper
    if len(word) > 0 or len(buffer) > 0:  # flush
        yield word + buffer
