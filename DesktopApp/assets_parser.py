import math
import operator
import os
import time
import logging
import xml.etree.ElementTree as ET

from DesktopApp.datum import Datum
from DesktopApp.progress import Progress

class AssetsParser:
    def __init__(self, csvPath, xmlPath, on_progress_updated) -> None:
        self.csvPath = csvPath
        self.xmlPath = xmlPath
        
        self.on_progress_updated = on_progress_updated

    def csvParseAssetFile(self, datumList):
        tic = time.perf_counter()

        # Opening csv
        logging.debug('Opening Asset Database')
        self.on_progress_updated(Progress("Reading from assets..."))
        
        # Counting lines in the file for keeping track of progress
        assets_csv = open(self.csvPath, 'r')
        
        lineCount = sum(1 for line in assets_csv)
        incAmt = math.ceil(lineCount / 20)
        
        # Now actually reading the file
        with open(self.csvPath, 'r') as assets_csv:
            datumList.sort(key=operator.attrgetter('pID'))

            logging.debug("Parsing Asset Database")
            # all items data
            count = 0
            idx = 0
            for line in assets_csv:
                count += 1
                if count >= incAmt:
                    count = 0
                    self.on_progress_updated(Progress(f"Looked at {count}/{lineCount} stored assets"))
                    logging.debug(f"{count}/{lineCount}")
                
                values = line.split(',')
                pID = values[0]
                gID = values[1]
                name = values[2].rstrip()

                for i in range(idx, len(datumList)):
                    if datumList[i].pID == pID:
                        datumList[i].gID = gID
                        datumList[i].name = name
                    elif datumList[i].pID > pID:
                        idx = i
                        break

            
            logging.debug("-|")
            
            toc = time.perf_counter()
            logging.debug(f"Parsed Asset.csv in {toc - tic:0.4f} seconds")
            self.on_progress_updated(Progress("Done looking at assets, for now..."))

            return datumList
        
    def is_float(self, value):
        try:
            float(value)
            return True
        except:
            return False
    
    def csvFindPossibleMatches(self, datumList):
        tic = time.perf_counter()

        # Opening csv
        logging.debug('Opening Asset Database')
        self.on_progress_updated(Progress("Reading from assets..."))
        
        # Counting lines in the file for keeping track of progress
        assets_csv = open(self.csvPath, 'r')
        
        lineCount = sum(1 for line in assets_csv)
        incAmt = math.ceil(lineCount / 20)
        
        # Now actually reading the file
        with open(self.csvPath, 'r') as assets_csv:
            datumList.sort(key=operator.attrgetter('pID'))

            logging.debug("Parsing Asset Database: ")
            # all items data
            count = 0
            idx = 0
            for line in assets_csv:
                count += 1
                if count >= incAmt:
                    count = 0
                    self.on_progress_updated(Progress(f"Looked at {count}/{lineCount} stored assets"))
                    logging.debug(f"{count}/{lineCount}")
                
                values = line.split(',')
                pID = values[0]
                gID = values[1]
                name = values[2].rstrip()

                for i in range(idx, len(datumList)):
                    if datumList[i].pID == pID and not self.is_float(name):
                        datumList[i].gID = gID
                        datumList[i].name = name
                        
                        try:
                            if name not in [x.name for x in datumList[i].item_candidates]:
                                datumList[i].item_candidates.append(Datum(pID, gID, name))
                        except: 
                            pass
                    # elif datumList[i].pID > pID:
                        # idx = i
                        # break

            
            logging.debug("-|")
            
            toc = time.perf_counter()
            logging.debug(f"Parsed Asset.csv in {toc - tic:0.4f} seconds")
            self.on_progress_updated(Progress("Done looking at assets, for now..."))

            return datumList

    def csvParseMetadataFile(self, srcPath):
        tic = time.perf_counter()

        files = []
        f = open(srcPath, "r")
        for l in f:
            d = l.split('.json')
            filename = d[0]+'.json'
            meta = d[1].split(',')
            tags = []
            for m in meta:
                if m.strip():
                    tags.append(m.strip())

            o = {}
            o['filename'] = filename
            o['tags'] = tags
            if tags and not 'trash' in tags:
                files.append(o)

        f.close()
        toc = time.perf_counter()
        logging.debug(f"Parsed Metadata.csv in {toc - tic:0.4f} seconds")

        return files
    
    
    def jsonParse(self, dataPath, srcPaths, getFunc):
        def parseFile(fullPath, filename, objList):
            logging.debug('Loading ' + filename)
            r = getFunc(fullPath)
            if r:
                r.filename = filename
                objList.append(r)

        objList = []
        if isinstance(srcPaths, str):
            srcPaths = [srcPaths]

        for srcPath in srcPaths:
            folderPath = os.path.join(dataPath, srcPath)
            if os.path.isdir(folderPath):
                for filename in os.listdir(folderPath):
                    f = os.path.join(folderPath, filename)
                    if os.path.isfile(f):
                        parseFile(f,filename,objList)
            elif os.path.isfile(folderPath):
                parseFile(folderPath,os.path.basename(srcPath),objList)
            else:
                logging.debug('File: ' + folderPath + " cannot be found")


        return objList



