# import required module
import json
import logging

class Merchant:
    def __init__(self):
        self.items = []
        self.filename = ""

    def __str__(self):
        ret = self.filename + '\n'
        for i in self.items:
            ret += str(i) + '\n'
        
        return ret

class Buyable:
    def __init__(self, pID, gID, name, value, currency, amount, chance):
        self.pID = pID
        self.gID = gID
        self.name = name
        self.value = value
        self.currency = currency
        self.amount = amount
        self.chance = chance
    
    def __str__(self):

        chance = ''
        if(self.chance < 100):
            chance = str(self.chance) + "% chance of "
        
        amt = ''
        if isinstance(self.amount, int):
            amt = str(self.amount) + 'x '
        elif isinstance(self.amount, str):
            amt = ''
        else:
            x = 0
            y = 0
            if 'm_Y' in self.amount:
                x = self.amount['m_X']
                y = self.amount['m_Y']
            elif 'y' in self.amount:
                x = self.amount['y']
                y = self.amount['x']
            else:
                logging.debug('Amount unknown: ' + self.amount)

            if y != 0:
                if x == y:
                    amt = str(x) + 'x '
                else:
                    amt = str(x) + '-' + str(y) + 'x '

        return "- " + chance + amt +  str(self.name) +  " @ " + str(self.value) + " " + self.currency

def getMerchant(jsonPath):
    # Opening JSON file
    f = open(jsonPath)
    data = json.load(f)

    merchant = Merchant()
    
    # Iterating through the json list
    for i in data['startingItems']:
        p = i['price']
        o = i['orbs']
        t = i['tickets']

        value = 0
        currency = ""
        if p > 0:
            value = p
            currency = "Coins"
        elif o > 0:
            value = o
            currency = "Mana Orbs"
        else:
            value = t
            currency = "Tickets"
        
        if 'isLimited' in i and i['isLimited']:
            amount = i['amount']
        else:
            amount = "Unlimited"
        chance = ('chance' in i and i['chance']) or 100
        
        merchant.items.append(
            Buyable(str(i['item']['m_PathID']), -1, '',
            str(value), currency, amount, chance)
        )

    
    # Iterating through the json list
    for r in data['randomShopItems']:
        for i in r['shopItems']:
            p = i['price']
            o = i['orbs']
            t = i['tickets']

            value = 0
            currency = ""
            if p > 0:
                value = p
                currency = "Coins"
            elif o > 0:
                value = o
                currency = "Mana Orbs"
            else:
                value = t
                currency = "Tickets"
            
            amount = i['amount']
            chance = ('chance' in i and i['chance']) or 100
            
            merchant.items.append(
                Buyable(str(i['item']['m_PathID']), -1, '',
                str(value), currency, amount, chance)
            )


    # Closing file
    f.close()

    return merchant
