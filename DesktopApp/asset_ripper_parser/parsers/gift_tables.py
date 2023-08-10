

from ast import List
from difflib import SequenceMatcher
from enum import Enum
import itertools
import logging
import pprint
import re
from DesktopApp.asset_ripper_parser.exported_file_parser import parse_exported_file
from DesktopApp.asset_ripper_parser.index_files import FileIndexer

class GiftLevel(Enum):
    Love = 'love'
    Like = 'like'
    Neutral = 'good'
    Dislike = 'dislike'
    Unique = 'unique'

class UniqueGiftResponse:
    def __init__(self, item_name, response):
        self.item_name = item_name
        self.response = response

class GiftTable:
    def __init__(self) -> None:
        self.npc_name = ""
        
        self.loved_items = []
        self.loved_responses = []
        self.loved_birthday_response = ""
        
        self.liked_items = []
        self.liked_responses = []
        self.liked_birthday_response = ""
        
        self.neutral_items = []
        self.neutral_responses = []
        self.neutral_birthday_response = ""
        
        self.disliked_items = []
        self.disliked_responses = []
        self.disliked_birthday_response = ""
        
        self.unique_items = []
    
    def __str__(self):
        result = [self.npc_name]
        result.append("{{NPC Gift Preferences")
        result.append(f"|loveResponse  = {', '.join(self.loved_responses)}")
        result.append(f"|love          = {', '.join(self.loved_items)}")
        result.append(f"|loveGroups    = [[:Category:Universally_Loved_Gifts|Universally Loved Items]]")
        
        result.append(f"|likeResponse  = {', '.join(self.liked_responses)}")
        result.append(f"|like          = {', '.join(self.liked_items)}")
        result.append(f"|likeGroups    = [[:Category:Universally_Liked_Gifts|Universally Liked Items]]")
        
        result.append(f"|goodResponse  = {', '.join(self.neutral_responses)}")
        result.append(f"|good          = {', '.join(self.neutral_items)}")
        
        result.append(f"|dislikeResponse = {', '.join(self.disliked_responses)}")
        result.append(f"|dislike       = {', '.join(self.disliked_items)}")
        result.append(f"|dislikeGroups = [[:Category:Universally_Disliked_Gifts|Universally Disliked Items]]")
        
        result.append("}}")
        
        grouped_unique_gifts = itertools.groupby(self.unique_items, lambda x: x.response)
        for key, group in grouped_unique_gifts:
            names = [x.item_name for x in group]
            if len(names) > 3:
                match = SequenceMatcher(None, names[0], names[1]).find_longest_match()
                common_words = names[0][match.a:match.a + match.size]
                if len(common_words.strip()) > 1 and common_words.strip()[0].isupper():
                    name = "Any " + names[0][match.a:match.a + match.size].strip()
                else:
                    name = ', '.join(names)
            else:
                name = ', '.join(names)
            result.append(f"{name}: {key}")
        
        return '\n'.join(result)
        
        
def clean_text(text):
    result = text.replace("<i>", "''").replace("</i>", "''").replace("</color>", "")
    return re.sub(r"<color=#[0-9]+>", "", result)

def parse_gift_section(indexer: FileIndexer, component, gift_level, gift_table):
    if gift_level != GiftLevel.Unique:
        parsed_items = []
        items = component[gift_level.value]
        if items == '[]':
            return gift_table
        
        for item in items:
            guid = item['guid']
            item_name = indexer.find_name_from_guid(guid)
            
            parsed_items.append(item_name)
            
        if gift_level == GiftLevel.Love:
            gift_table.loved_items = parsed_items
            gift_table.loved_responses = [clean_text(x) for x in component[f'{gift_level.value}Responses']]
        elif gift_level == GiftLevel.Like:
            gift_table.liked_items = parsed_items
            gift_table.liked_responses = [clean_text(x) for x in component[f'{gift_level.value}Responses']]
        elif gift_level == GiftLevel.Neutral:
            gift_table.neutral_items = parsed_items
            gift_table.neutral_responses = [clean_text(x) for x in component[f'{gift_level.value}Responses']]
        elif gift_level == GiftLevel.Dislike:
            gift_table.disliked_items = parsed_items
            gift_table.disliked_responses = [clean_text(x) for x in component[f'{gift_level.value}Responses']]
    else:
        parsed_items = []
        items = component['uniqueGifts']
        for item in items:
            guid = item['item']['guid']
            item_name = indexer.find_name_from_guid(guid)
            response = item['response']
            
            parsed_items.append(UniqueGiftResponse(item_name, clean_text(response)))
            
        gift_table.unique_items = parsed_items
    return gift_table

def parse_gift_tables(indexer: FileIndexer, filepaths: list[str], report_progress=None):
    tables = []
    for path in filepaths:
        gift_table = GiftTable()
        gift_table.npc_name = path.split("gift tables\\")[1].replace("GiftTable.asset", "")
        try:
            components = parse_exported_file(path)
            main_component = components[0]['MonoBehaviour']
            
            for gift_level in list(GiftLevel):
                try:
                    gift_table = parse_gift_section(indexer, main_component, gift_level, gift_table)
                    # pprint.pprint(main_component)
                except:
                    logging.error(f"Could not get {gift_level.value} gifts for {path}", exc_info=True)
                    pprint.pprint(main_component)
                    
            for i in range(0, len(main_component['birthdayResponses'])):
                if i == 0:
                    gift_table.disliked_birthday_response = main_component['birthdayResponses'][i]
                elif i == 1:
                    gift_table.liked_birthday_response = main_component['birthdayResponses'][i]
                elif i == 2:
                    gift_table.loved_birthday_response = main_component['birthdayResponses'][i]
                
            if report_progress is not None:
                report_progress()
            tables.append(gift_table)
        except:
            logging.error(f"Couldn't parse {path}", exc_info=True)
            
    return tables
            

