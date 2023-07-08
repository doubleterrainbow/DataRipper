# import required module
import json
import os
import logging

import DesktopApp.Modules.SunHaven_Utilities as utils

class Quest:
    RequirementTypes = {}
    RequirementTypes[2] = 'Items'
    RequirementTypes[4] = 'Progress'
    RequirementTypes[8] = 'Token'

    def __init__(self):
        self.inputs = []
        self.kills = []
        self.rewards = []
        self.choiceRewards = []
        self.filename = ""

        self.name = ""
        self.turnInNpc = ""
        self.bbDescription = ""
        self.description = ""
        self.requirementType = ""
        self.endText = ""

        self.characterProgressRequirements = []
        self.questProgressRequirements = []
        self.worldProgressRequirements = []
    
    def __str__(self):
        ret = self.filename + ' - ' + self.name + '\n'
        ret += ':Requirements\n'
        ret += '- TurnIn: ' + self.turnInNpc + '\n'
        if self.requirementType in self.RequirementTypes:
            ret += '- Type: ' + str(self.RequirementTypes[self.requirementType]) + '\n'
        
        if self.characterProgressRequirements:
            ret += '- Character Progression \n'
            for req in self.characterProgressRequirements:
                ret += "-- "+ str(req) + '\n'
        if self.questProgressRequirements:
            ret += '- Quest Progression \n'
            for req in self.questProgressRequirements:
                ret += "-- "+ str(req) + '\n'
        if self.worldProgressRequirements:
            ret += '- World Progression \n'
            for req in self.worldProgressRequirements:
                ret += "-- "+ str(req) + '\n'

        ret += ':Text\n'
        ret += '- BB: ' + utils.subPlayerName(utils.wikifyColorTags(self.bbDescription)) + '\n'
        ret += '- Quest: ' + utils.subPlayerName(utils.wikifyColorTags(self.description)) + '\n'
        ret += '- End: ' + utils.subPlayerName(utils.wikifyColorTags(self.endText)) + '\n'

        if self.inputs:
            ret += ':Items\n'
            for item in self.inputs:
                ret += "- "+ str(item) + '\n'
        if self.kills:
            ret += ':Kills\n'
            for item in self.kills:
                ret += "- "+ str(item) + '\n'
        ret += ':Rewards:\n'
        for item in self.rewards:
            ret += "- "+ str(item) + '\n'
        ret += ':Choices:\n'
        for item in self.choiceRewards:
            ret += "- "+ str(item) + '\n'

        return ret

class Item:
    def __init__(self, pID, gID, name, amount):
        self.pID = pID
        self.gID = gID
        self.name = name
        self.amount = amount
    
    def __str__(self):
        return str(self.amount) + "x " + self.name

class Requirement:
    def __init__(self, pID, gID, name):
        self.pID = pID
        self.gID = gID
        self.name = name
    
    def __str__(self):
        return self.name

def getQuest(jsonPath):
    # Opening JSON file
    f = open(jsonPath)
    data = json.load(f)

    obj = Quest()
    
    if not ('questName' in data):
        logging.debug('Unhandled Quest: ' + os.path.basename(jsonPath))
        return

    obj.name = data['questName']
    obj.turnInNpc = data['npcToTurnInTo']
    obj.bbDescription = data['bulletinBoardDescription']

    if (not data['questDescription']) and 'overrideTurnInText' in data:
        obj.description = data['overrideTurnInText']
    else: 
        obj.description = data['questDescription']
    
    obj.requirementType = data['questRequirements']

    if 'characterProgressRequirements' in data and data['characterProgressRequirements']:
        for i in data['characterProgressRequirements']:
            obj.characterProgressRequirements.append(
                Requirement(str(i['m_PathID']),-1,'')
            )
    if 'questProgressRequirements' in data and data['questProgressRequirements']:
        for i in data['questProgressRequirements']:
            obj.questProgressRequirements.append(
                Requirement(-1,-1,i['progressName'])
            )
    if 'worldProgressRequirements' in data and data['worldProgressRequirements']:
        for i in data['worldProgressRequirements']:
            obj.worldProgressRequirements.append(
                Requirement(str(i['m_PathID']),-1,'')
            )

    obj.endText = data['endTex']

    # Iterating through the json list
    for d in data['itemRequirements']:
        for i in d['items']:
            obj.inputs.append(
                Item(str(i['item']['m_PathID']), -1, '', i['amount'])
            )
    # Iterating through the json list
    for i in data['killRequirements']:
        obj.kills.append(
            Item(-1, -1, i['enemy'], i['killAmount'])
        )
    # Iterating through the json list
    for i in data['guaranteeRewards']:
        obj.rewards.append(
            Item(str(i['item']['m_PathID']), -1, '', i['amount'])
        )
    # Iterating through the json list
    for i in data['giveItemsOnComplete']:
        obj.rewards.append(
            Item(str(i['item']['m_PathID']), -1, '', i['amount'])
        )
    # Iterating through the json list
    for i in data['choiceRewards']:
        obj.choiceRewards.append(
            Item(str(i['item']['m_PathID']), -1, '', i['amount'])
        )

    # Closing file
    f.close()

    return obj
