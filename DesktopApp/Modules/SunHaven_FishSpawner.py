# import required module
import json

from DesktopApp.datum import Datum

class FishSpawner:
    def __init__(self):
        self.drops = []
        self.filename = ''
        self.location = Datum("", -1, "") 
    
    def _lerp(self, a: float, b: float, t: float) -> float:
        """Linear interpolate on the scale given by a to b, using t as the point on that scale.
        Examples
        --------
            50 == lerp(0, 100, 0.5)
            4.2 == lerp(1, 5, 0.8)
        """
        return (1 - t) * a + t * b


    def _adjusted_odds_based_on_rarity_and_level(self, rarity, level):
        if rarity == 'Rare':
            return self._lerp(0.8, 3.35, level / 120)
        elif rarity == 'Epic':
            return self._lerp(0.675, 4.25, level / 120)
        elif rarity == 'Legendary':
            return self._lerp(0.55, 5, level / 120)
        else:
            return 1
    
    def _calculate_percentages(self, drops, level, familiar_waters_value=0.0, advanced_fish_mapping_value=0.0):
        result = []
        
        num = 0.0
        num2 = 0.0
        if familiar_waters_value:
            num += 0.05 * familiar_waters_value
        if advanced_fish_mapping_value:
            num2 += 0.1 * advanced_fish_mapping_value
        
        total_probability = 0.0
        for fish_loot in drops:
            num3 = 1.0
            fish_rarity = fish_loot.rarity
            if fish_rarity == 'Epic':
                num3 += num
            elif fish_rarity == 'Legendary':
                num3 += num + num2
            
            adjusted_odds = self._adjusted_odds_based_on_rarity_and_level(fish_loot.rarity, level)
            total_probability += fish_loot.chance * num3 * adjusted_odds
        
        num5 = 0.0
        for fish_loot in drops:
            rarity_adjustment = 1.0
            fish_rarity = fish_loot.rarity
            if fish_rarity == 'Epic':
                rarity_adjustment += num
            elif fish_rarity == 'Legendary':
                rarity_adjustment += num + num2
            
            adjusted_odds = self._adjusted_odds_based_on_rarity_and_level(fish_loot.rarity, level)
            num5 = fish_loot.chance * rarity_adjustment * adjusted_odds
            
            result.append({
                'path_id': fish_loot.pID,
                'percent': (num5 / total_probability) * 100,
            })

        return result
    
    def _calculate_min_max_percents(self):
        for season in ['All', 'Spring', 'Summer', 'Fall', 'Winter']:
            seasonal_drops = [drop for drop in self.drops if drop.season == season]
            
            min_percents = self._calculate_percentages(seasonal_drops, level=1)
            max_percents = self._calculate_percentages(
                seasonal_drops,
                level=70, 
                familiar_waters_value=15, 
                advanced_fish_mapping_value=30
            )
            
            for drop in seasonal_drops:
                matching_min = [fish for fish in min_percents if fish['path_id'] == drop.pID]
                if matching_min:
                    drop.min_percent_chance = matching_min[0]['percent']
                    
                matching_max = [fish for fish in max_percents if fish['path_id'] == drop.pID]
                if matching_max:
                    drop.max_percent_chance = matching_max[0]['percent']
    
    def calculate_percent_chance(self):
        self._calculate_min_max_percents()
        
    def __str__(self) -> str:
        result = f"{self.filename}\n"
        
        if self.location.name:
            result += f"{self.location.name.rstrip()}"
        
        for drop in self.drops:
            result += f"\n{drop.season}: {drop.name} {round(drop.min_percent_chance, 2)}% -> {round(drop.max_percent_chance, 2)}%"
            
        return result
    
class FishSpawnable:
    def __init__(self, pID, gID, name, chance, season):
        self.pID = pID
        self.gID = gID
        self.name = name
        self.chance = chance
        self.season = season
        self.rarity = 'Common'
        self.min_percent_chance = 0.0
        self.max_percent_chance = 0.0
        
    def __str__(self) -> str:
        return f"{self.season}: {self.name} {round(self.min_percent_chance, 2)}% -> {round(self.max_percent_chance, 2)}%"

def getFishSpawner(jsonPath) -> FishSpawner:
    # Opening JSON file
    f = open(jsonPath)
    data = json.load(f)
    
    spawner = FishSpawner()
    
    spawner.location.pID = data["m_GameObject"]["m_PathID"]
    
    # Iterating through the json list
    for i in data['fish']['drops']:
        spawner.drops.append(
            FishSpawnable(str(i['fish']['m_PathID']), -1, '',
            float(i['dropChance']), 'All')
        )

    if data['hasSeasonalFish']:
        for i in data['fishSpring']['drops']:
            spawner.drops.append(
                FishSpawnable(str(i['fish']['m_PathID']), -1, '',
                float(i['dropChance']), 'Spring')
            )
        for i in data['fishSummer']['drops']:
            spawner.drops.append(
                FishSpawnable(str(i['fish']['m_PathID']), -1, '',
                float(i['dropChance']), 'Summer')
            )
        for i in data['fishFall']['drops']:
            spawner.drops.append(
                FishSpawnable(str(i['fish']['m_PathID']), -1, '',
                float(i['dropChance']), 'Fall')
            )
        for i in data['fishWinter']['drops']:
            spawner.drops.append(
                FishSpawnable(str(i['fish']['m_PathID']), -1, '',
                float(i['dropChance']), 'Winter')
            )

    # Closing file
    f.close()

    return spawner
