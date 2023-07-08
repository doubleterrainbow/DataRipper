# import required module
import json

class GiftTable:
  def __init__(self):
    self.loveResponses = []
    self.love = []
    self.likeResponses = []
    self.like = []
    self.goodResponses = []
    self.good = []
    self.dislikeResponses = []
    self.dislike = []
    self.unique = []
    self.birthdayResponses = []
    self.birthMonth = ""
    self.birthDay = ""
    self.filename = ""

class Giftable:
  def __init__(self, pID, gID, name, tier, response):
    self.pID = pID
    self.gID = gID
    self.name = name
    self.tier = tier
    self.response = response

def getGiftTable(jsonPath):
    # Opening JSON file
    f = open(jsonPath)
    data = json.load(f)

    obj = GiftTable()
    
    # Iterating through the json list
    for i in data['love']:
        obj.love.append(
            Giftable(str(i['m_PathID']), -1, '', "love", "")
        )
    for i in data['like']:
        obj.like.append(
            Giftable(str(i['m_PathID']), -1, '', "like", "")
        )
    for i in data['good']:
        obj.good.append(
            Giftable(str(i['m_PathID']), -1, '', "good", "")
        )
    for i in data['dislike']:
        obj.dislike.append(
            Giftable(str(i['m_PathID']), -1, '', "dislike", "")
        )
    for i in data['uniqueGifts']:
        obj.unique.append(
            Giftable(str(i['item']['m_PathID']), -1, '', "unique", i['response'])
        )
    for i in data['loveResponses']:
        obj.loveResponses.append(i)
    for i in data['likeResponses']:
        obj.likeResponses.append(i)
    for i in data['goodResponses']:
        obj.goodResponses.append(i)
    for i in data['dislikeResponses']:
        obj.dislikeResponses.append(i)
    for i in data['birthdayResponses']:
        obj.birthdayResponses.append(i)
    obj.birthMonth = str(data['birthMonth'])
    obj.birthDay = str(data['birthDay'])

    # Closing file
    f.close()

    return obj
