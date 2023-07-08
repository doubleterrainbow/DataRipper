# import required module
import os
import logging

class Dialogue:
  def __init__(self):
    self.oneliner = None
    self.cycle = None
    self.filename = ""

    self.npc = ""
    self.occurance = ""

def getDialogue(filePath):
    lines = []
    filename = os.path.basename(filePath)
    with open(filePath, encoding="utf8") as file:
        lines = [line.strip() for line in file]
        lines = [line for line in lines if line]

    obj = Dialogue()

    # Cycle
    if 'Cycle' in lines[0] or \
       'Charon' in filename or \
       'PostMarriage' in lines[0] or \
       'MailQuest' in lines[0]:

        cycle = {}

        if 'Cycle' in lines[0]:
            splitIdx = lines[0].index('Cycle')
            obj.npc = lines[0][:splitIdx].strip()
            obj.occurance = lines[0][splitIdx:]
        elif 'Charon' in filename:
            obj.npc = 'Charon'
            obj.occurance = filename[filename.index('Charon')+6:-4]
        elif 'PostMarriage' in lines[0]:
            tok = lines[0].split('Quest')
            obj.npc = tok[1][:-1]
            obj.occurance = 'Post Marriage Quest'
        elif 'MailQuest' in lines[0]:
            tok = lines[0].split('Mail')
            obj.npc = tok[0]
            obj.occurance = 'Mail Quest'
        splitIdx = None

        for idx in range(1, len(lines)):
            if '::' in lines[idx]:
                splitIdx = lines[idx].index('::')
                cycle[lines[idx][:splitIdx]] = lines[idx][splitIdx+2:].replace('XX', '[Player]').replace('[]', '<br>').strip()
            elif lines[idx] == 'End':
                break
            else:
                if splitIdx:
                    cycle[lines[idx-1][:splitIdx]] += lines[idx].replace('XX', '[Player]').replace('[]', '<br>').strip()
                else:
                    logging.debug('Unhandled line in ' + filePath + ':\n- ' + lines[idx])

        obj.cycle = cycle
    else:
        tag = ""
        if 'Intro' in lines[0]:
            tag = 'Intro'
        elif 'One' in lines[0]:
            tag = 'One'
        
        oneliner = []

        if tag:
            splitIdx = lines[0].index(tag)
            obj.npc = lines[0][:splitIdx].strip()
            obj.occurance = lines[0][splitIdx:]
        else:
            obj.npc = 'Unknown'
            obj.occurance = lines[0]
        
        for idx in range((1 if tag else 0), len(lines)):
            if '::' in lines[idx]:
                splitIdx = lines[idx].index('::')
            elif lines[idx].startswith(':'):
                splitIdx = 0
            elif lines[idx] == 'End':
                break
            else:
                logging.debug('Unhandled line in ' + filePath + ':\n- ' + lines[idx])
                continue

            oneliner.append(lines[idx][splitIdx+2:].replace('XX', '[Player]').replace('[]', '<br>').strip())

        obj.oneliner = oneliner

    return obj
