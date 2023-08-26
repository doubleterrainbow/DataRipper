import logging
import yaml


def parse_exported_file(filepath, only_with_text=None):
    """Returns a list of dicts containing parsed yaml.
    List sections are split on the "--- !u!" line.

    There can be multiple "MonoBehaviour" sections.

    Args:
        filepath (str): path of file to parse
        only_with_text (str, optional): will not parse any sections without this text.
                                        When this is None, all sections will be parsed.
                                        Mostly used for scene files.
                                        Defaults to None.

    Returns:
        list[dict]: list of dicts, each containing a section from the asset ripper file.
    """
    parsed_sections = []
    # logging.debug(f"Parsing {filepath}")

    with open(filepath, "r", encoding="utf-8") as prefab_file:
        lines = prefab_file.readlines()

        sections = []

        section = ""
        upcoming_section_marker = True
        for line in lines:
            try:
                if line.startswith("%YAML 1.1") or line.startswith("%TAG"):
                    continue

                if line.startswith("--- !u!"):
                    upcoming_section_marker = True
                    continue

                if upcoming_section_marker:
                    if section.strip() != "":
                        sections.append(section)

                    section = line + "\n"
                    upcoming_section_marker = False
                else:
                    section += line + "\n"
                    upcoming_section_marker = False
            except:
                logging.error("Could not parse line: %s", line, exc_info=True)

        sections.append(section)

        for section in sections:
            try:
                if only_with_text is not None and only_with_text not in section:
                    continue
                data = yaml.safe_load(section)
                parsed_sections.append(data)
            except yaml.YAMLError:
                logging.error("Error parsing YAML %s", filepath, exc_info=True)

    return parsed_sections
