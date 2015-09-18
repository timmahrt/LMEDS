'''
Created on Dec 29, 2013

@author: tmahrt
'''

import codecs

from lmeds.io import sequence
HEADER_DEMARCATOR = ";,"  # Splits the header from its data


def loadUserResponse(fn):
    
    with codecs.open(fn, "rU", encoding="utf-8") as fd:
        featureList = fd.read().split("\n")
        
    returnList = []
    for line in featureList:
        if line == "":
            continue
        
        if line[-2:] == HEADER_DEMARCATOR:
            header = line[:-2]
            dataTxt = ""
        else:
            header, dataTxt = line.split(HEADER_DEMARCATOR)
        
        command, argTxt = header.split(",", 1)
        stimuliArgs, metaData = argTxt.rsplit("],", 1)
        stimuliArgs = stimuliArgs.strip()[1:]  # Remove leading '['
        
        # HACK: Why are quote marks around every item in the output?
        stimuliArgs = stimuliArgs.replace("'", "")
        stimuliArgList = sequence.recChunkLine(stimuliArgs, ',')
        
        returnList.append((command, stimuliArgList, metaData, dataTxt))
    
    return returnList
