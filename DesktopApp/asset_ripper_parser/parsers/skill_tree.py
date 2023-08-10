

import logging
import pprint
from DesktopApp.asset_ripper_parser.exported_file_parser import parse_exported_file
from DesktopApp.asset_ripper_parser.index_files import FileIndexer
from DesktopApp.asset_ripper_parser.parsers.parse_sprite_sheet import Sprite, parse_sprite_asset

class Skill:
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
    def __init__(self):
        self.name = ""
        self.skills: list[Skill] = []
        
    def __str__(self):
        return self.name + "\n" + '\n\n'.join([str(skill) for skill in self.skills])
        
def camel_case_split(s):
    u = True  # case of previous char
    w = b = ''  # current word, buffer for last uppercase letter
    for c in s:
        o = c.isupper()
        if u and o:
            w += b
            b = c
        elif u and not o:
            if len(w)>0:
                yield w
            w = b + c
            b = ''
        elif not u and o:
            yield w
            w = ''
            b = c
        else:  # not u and not o:
            w += c
        u = o
    if len(w)>0 or len(b)>0:  # flush
        yield w + b
        

def parse_skill_trees(
    indexer: FileIndexer,
    filepaths: list[str],
    skill_filepaths: list[str],
    report_progress=None
):
    trees = []
    for path in filepaths:
        tree = SkillTree()
        tree.name = ' '.join(camel_case_split(path.split('\\')[-1].replace(".asset", "")))
        try:
            components = parse_exported_file(path)
            main_component = components[0]['MonoBehaviour']
            try:
                skills = []
                referenced_skills = main_component['serializationData']['ReferencedUnityObjects']
                
                for item in referenced_skills:
                    skill_filename = indexer.find_filepath_from_guid(item['guid'])
                    matching_path = [x for x in skill_filepaths if skill_filename is not None and skill_filename in x]
                    if matching_path:
                        skill_components = parse_exported_file(matching_path[0])
                        skill_component = skill_components[0]['MonoBehaviour']
                        
                        skill = Skill()
                        skill.name = skill_component['nodeName']
                        skill.title = skill_component['nodeTitle']
                        skill.points = skill_component['nodePoints']
                        skill.description = skill_component['description']
                        
                        skill_sprite_path = indexer.find_sprite_path_from_guid(skill_component['icon']['guid'])
                        if skill_sprite_path is not None:
                            skill.sprite = parse_sprite_asset(indexer, skill_sprite_path)

                        try:
                            if "ITEM1" in skill.description:
                                skill.description = skill.description.replace("ITEM1", str(skill_component['descriptionItems'][0]))

                            if "ITEM2" in skill.description:
                                skill.description = skill.description.replace("ITEM2", str(skill_component['descriptionItems'][1]))

                            if "ITEM3" in skill.description:
                                skill.description = skill.description.replace("ITEM3", str(skill_component['descriptionItems'][2]))

                            if "ITEM4" in skill.description:
                                skill.description = skill.description.replace("ITEM4", str(skill_component['backupdescriptionItems'][0]))

                            if "ITEM5" in skill.description:
                                skill.description = skill.description.replace("ITEM5", str(skill_component['backupdescriptionItems'][1]))

                            if "ITEM6" in skill.description:
                                skill.description = skill.description.replace("ITEM6", str(skill_component['backupdescriptionItems'][2]))
                            
                            if "UNLOCK" in skill.description:
                                skill.description = skill.description.replace("UNLOCK", str(skill_component['singleDescriptionItem']))
                        except:
                            logging.error(f"Unable to populate description placeholders for {skill.title}")
                        
                        skills.append(skill)
                
                if report_progress is not None:
                    report_progress()
                
                tree.skills = skills
                trees.append(tree)
            except:
                pprint.pprint(main_component)
                logging.error(f"Couldn't parse {tree.name}", exc_info=True)
        except:
            logging.error(f"Couldn't parse {path}", exc_info=True)
            
    return trees
            


