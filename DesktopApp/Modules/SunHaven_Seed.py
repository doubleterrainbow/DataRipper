
import json
import logging
import math
import re

class Seed:
    def __init__(self):
        self.name = ""
        self.crop_name = ""
        self.days_to_grow = 0.0
        self.coin_sell_price = 0.0
        self.orb_sell_price = 0.0
        self.ticket_sell_price = 0.0
        self.buy_price = 0.0
        self.region = "Sun Haven"
        self.crop_yield = 1
        self.exp = 0.0
        self.seasons = []
        self.infusable = False
        self.regrowable = False
        self.regrow_days = 1.0
        
    def __str__(self):
        result = [self.name]
        
        result.append(f"Yield = {self.crop_yield}")
        result.append(f"Days = {self.days_to_grow}")
        result.append(f"Sells for = {self.coin_sell_price} Coins, {self.orb_sell_price} Orbs, {self.ticket_sell_price} Tickets")
        result.append(f"Exp = {self.exp}")
        result.append(f"Seasons = {self.seasons}")
        
        if self.infusable:
            result.append(f"Infuse Needed")
            
        if self.regrowable:
            result.append(f"Regrows in {self.regrow_days} days")
        
        return "\n".join(result)
    
    def to_csv(self):
        return f"{self.name},{self.crop_yield},{self.days_to_grow},{self.coin_sell_price},Coins,{self.exp},{'|'.join([str(x) for x in self.seasons])},{self.infusable},{self.regrowable},{self.regrow_days}"
    
    def to_wiki_tags(self):
        result = ["{{Harvest summary"]
        
        result.append(f"|name = {self.crop_name}")
        result.append(f"|region = {self.region}")
        result.append(f"|seed = {self.name}")
        result.append(f"|exp = {self.exp}")
        result.append(f"|growth = {self.days_to_grow}")
        result.append(f"|regrowthRate = {str(self.regrow_days) if self.regrowable else ''}")
        result.append(f"|cropYield = {self.crop_yield}")
        
        max_harvest = 1
        if self.regrowable:
            max_harvest = math.floor((((len(self.seasons) * 28) - (self.days_to_grow + 1)) / self.regrow_days) + 1)
        result.append(f"|maxHarvest = {max_harvest}")
        
        season_labels = []
        if 0 in self.seasons:
            season_labels.append("Spring")
        if 1 in self.seasons:
            season_labels.append("Summer")
        if 2 in self.seasons:
            season_labels.append("Fall")
        if 3 in self.seasons:
            season_labels.append("Winter")
            
        if len(season_labels) == 4:
            season_label = "Any"
        else:
            season_label = " and ".join(season_labels)
        
        
        result.append(f"|season = {season_label}")
        result.append(f"|seedPrice = {str(self.buy_price) if self.buy_price > 0 else ''}")
        
        sell_price = self.coin_sell_price
        if self.orb_sell_price > 0:
            sell_price = self.orb_sell_price
        elif self.ticket_sell_price > 0:
            sell_price = self.ticket_sell_price
            
        result.append(f"|cropSell = {sell_price}")
        
        result.append("}}")
        
        return '\n'.join(result)
                

def getSeed(jsonPath):
    # Opening JSON file
    f = open(jsonPath)
    data = json.load(f)

    seed = Seed()
    seed.name = data['name']
    
    crop_match = re.search(r"^([A-Z][a-z]+\s)+(?=Seeds)?", data['helpDescription'])
    if crop_match is not None:
        seed.crop_name = crop_match[0]
    else:
        seed.crop_name = seed.name
        
    seed.crop_name = seed.crop_name.replace("Seeds", "").strip()
    
    coins_match = re.search(r'([0-9]+) <sprite=\"gold_icon', data['helpDescription'])
    if coins_match is not None:
        seed.coin_sell_price = int(coins_match.group(1))
    
    tickets_match = re.search(r'([0-9]+) <sprite=\"ticket_icon', data['helpDescription'])
    if tickets_match is not None:
        seed.ticket_sell_price = int(tickets_match.group(1))
    
    orbs_match = re.search(r'([0-9]+) <sprite=\"orb_icon', data['helpDescription'])
    if orbs_match is not None:
        seed.orb_sell_price = int(orbs_match.group(1))
    
    yield_match = re.search(r"yield[<>=a-zA-Z\s]+([0-9]+)", data['helpDescription'])
    if yield_match is not None:
        seed.crop_yield = int(yield_match.group(1))
    
    seed.region = "Sun Haven"
    if 'coin' in data['helpDescription']:
        # weird duplicate logic to account for Soul Orbs and Sun Orbs
        seed.region = "Sun Haven"
    elif 'orb' in data['helpDescription']:
        seed.region = "Nel'Vari"
    elif 'ticket' in data['helpDescription']:
        seed.region = "Withergate"
    
    if data['cropStages']:
        seed.days_to_grow = int(data['cropStages'][-1]["daysToGrow"])
    
    seed.exp = int(data['exp'])
    seed.seasons = data['seasons']
    
    seed.regrowable = data['regrowable']
    seed.infusable = data['manaInfusable']
    seed.regrow_days = int(data['daysToRegrow'])
    
    # Closing file
    f.close()

    return seed
