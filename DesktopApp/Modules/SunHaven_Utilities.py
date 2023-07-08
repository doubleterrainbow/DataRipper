# import required module
import os

def wikifyColorTags(line):
    v = line.replace('<color=', '<span style="color: ')
    v = v.replace('</color>','</span>')
    return v

def subPlayerName(line):
    return line.replace('XX', '[Player]')