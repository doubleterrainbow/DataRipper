import json
import logging
import re

def parse_line(line):
    if "{" not in line:
        try:
            return int(line.strip())
        except ValueError:
            return line.strip()
    
    if line.strip() == "[]":
        return []
    
    result = {}
    
    clean_line = line.replace("{", "").replace("}", "").strip()
    
    items = clean_line.split(",")
    for item in items:
        key_value = item.strip().split(':', 1)
        if len(key_value) == 2:
            result[key_value[0].strip()] = key_value[1].strip()
            
    return result

def parse_section(section):
    result = {}
    section_title = section.split('\n')[0].replace(":", "").strip()
    result['type'] = section_title
    
    subsection = {}
    level = 1
    default_leading_spaces = 2
    last_key = None
    
    list_item = {}
    
    # if at level 1,
    #   apply subsection if applicable
    #   apply key:value to result
    # if at 2nd level, apply key:value to subsection
    # if at - level, add/create a list with list_item
    #   apply key:value to list_item
    
    for line in [x for x in section.split('\n') if x.strip() != ""]:
        leading_spaces = len(line) - len(line.lstrip())
        level = leading_spaces / default_leading_spaces
        
        if level == 1 and line.strip().startswith("-"):
            if list_item != {}:
                if last_key not in result or not isinstance(result[last_key], list):
                    result[last_key] = []
                    
                result[last_key].append(list_item)
                list_item = {}

            value = parse_line(line.replace("-", "").strip())
            list_item = value
        elif level == 1:
            if subsection != {}:
                result[last_key] = subsection
                subsection = {}
            elif list_item != {}:
                try:
                    result[last_key].append(list_item)
                    list_item = {}
                except:
                    pass
            
            key_value = line.split(":", 1)
            key = key_value[0].strip()
        
            last_key = key
            list_item = {}
        
            if len(key_value) > 1:
                result[key] = parse_line(key_value[1])
                
        elif level == 2:
            key_value = line.strip().split(":", 1)
            key = key_value[0].strip()
            
            if len(key_value) == 1:
                value = ""
            else:
                value = parse_line(key_value[1])
            
            subsection[key] = value
    return result
    

def parse_prefab(filepath):
    components = []
    
    logging.debug(f"Parsing {filepath}")
    
    with open(filepath, 'r') as prefab_file:
        lines = prefab_file.readlines()
        
        upcoming_section_marker = False
        
        component = {}
        sections = []
        
        section = ""
        
        for line in lines:
            upcoming_section_marker = line.startswith("--- !u!")
            
            try:
                if line.startswith("%YAML 1.1") or line.startswith("%TAG") or line.startswith("--- !u!"):
                    continue
                elif upcoming_section_marker:
                    if section.strip() != "":
                        sections.append(section)
                        
                    section = line + "\n"
                else:
                    section += line + "\n"
            except:
                logging.error(f"Could not parse line: {line}", exc_info=True)
                
        sections.append(section)
        
        for section in sections:
            component = parse_section(section)
            components.append(component)
    return components
