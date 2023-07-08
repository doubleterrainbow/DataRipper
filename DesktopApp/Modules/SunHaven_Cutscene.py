# import required module
import os

class Cutscene:
    def __init__(self):
        self.text = None
        self.filename = ""

    def __str__(self):
        ret = str(self.filename) + ': \n'
        for t in self.text:
            ret += t + '\n'

        return ret

def getCutscene(filePath):
    obj = {}
    lines = []
    filename = os.path.basename(filePath)
    with open(filePath, encoding="utf8") as file:
        lines = [line.strip() for line in file]
        #lines = [line for line in lines if ('TranslateObject(' in line or 'TranslateNPCName(' in line)]

    text = []
    for line in lines:
        lineStartIdx = 0
        lineEndIdx = len(line)
        if 'TranslateObject(' in line:
            lineStartIdx = line.index('TranslateObject(')+17
            lineEndIdx = line.index('"', lineStartIdx)
            l = line[lineStartIdx:lineEndIdx]
        elif 'TranslateNPCName(' in line:
            lineStartIdx = line.index('TranslateNPCName(')+17
            lineEndIdx = line.index(')', lineStartIdx)
            l = line[lineStartIdx:lineEndIdx]
            if l.startswith('this.'):
                l = l.split('.')[1]
        else:
            continue

        if 'ValueTuple<string, UnityAction>(' in line:
            l = "> " + l
        text.append(l)

    if len(text) > 0:
        obj = Cutscene()
        obj.text = text

    return obj
