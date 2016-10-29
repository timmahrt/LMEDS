'''
Created on Dec 29, 2013

@author: tmahrt
'''

import io

from lmeds.lmeds_io import sequence
HEADER_DEMARCATOR = ";,"  # Splits the header from its data


def loadUserResponse(fn):
    
    with io.open(fn, "r", encoding="utf-8") as fd:
        featureList = [row.rstrip('\n') for row in fd.readlines()]
    
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
        
        stimuliArgList = sequence.recChunkLine(stimuliArgs, ',')
        
        returnList.append((command, stimuliArgList, metaData, dataTxt))
    
    return returnList
