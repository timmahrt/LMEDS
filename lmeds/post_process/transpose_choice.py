'''
Created on Aug 21, 2015

@author: tmahrt
'''

import os
from os.path import join
import codecs

from lmeds.io import user_response
from lmeds.utilities import utils


def _buildHeader(fnList, numArgs, pageName):
    # Build the name lists, which will take up the first two rows in the
    # spreadsheet.  One is normal, and one is anonymized
    oom = utils.orderOfMagnitude(len(fnList))
    userNameTemplate = "t%%0%dd.%s" % (oom + 1, pageName)
    
    nameList = [os.path.splitext(name)[0] + "." + pageName for name in fnList]
    anonNameList = [userNameTemplate % (i + 1)
                    for i in xrange(len(fnList))]
    
    headerPrefixList = ["stimulusID", ]
    headerPrefixList += ["arg%d" % (i + 1) for i in xrange(numArgs)]
    
    nameList = headerPrefixList + nameList
    anonNameList = headerPrefixList + anonNameList
    
    return nameList, anonNameList
    

def transposeChoice(path, pageName, outputPath):
    
    utils.makeDir(outputPath)
    
    # Load choice data
    choiceDataList = []
    fnList = utils.findFiles(path, filterExt=".csv")
    for fn in fnList:
        a = user_response.loadUserResponse(join(path, fn))
        choiceDataList.append(a)
    
    # Convert response to single answer
    responseDataList = []
    stimuliList = []
    stimuliListsOfLists = []
    for userDataList in choiceDataList:
        userResponse = [str(responseTuple[3].split(',').index('1'))
                        for responseTuple in userDataList]
        responseDataList.append(userResponse)
    
        userStimuli = [",".join(responseTuple[1])
                       for responseTuple in userDataList]
        if stimuliList == []:
            stimuliList = userStimuli
        stimuliListsOfLists.append(userStimuli)
    
    # Assert all the headers are the same for each user
    assert(all([stimuliListsOfLists[0] == header
                for header in stimuliListsOfLists]))
    
    # Transpose data
    tResponseDataList = [row for row in utils.safeZip(responseDataList, True)]
    
    # Add stimuli information to each row
    outputList = [[header, ] + list(row) for header, row
                  in utils.safeZip([stimuliList, tResponseDataList], True)]

    # Add a unique id to each row
    oom = utils.orderOfMagnitude(len(stimuliList))
    stimID = "s%%0%dd" % (oom + 1)
    outputList = [[stimID % i, ] + row for i, row in enumerate(outputList)]
    
    # Add the column heading rows
    # First row in unanonymized user names
    # Second row is anonymized
    numArgs = stimuliList[0].count(",") + 1
    rowOne, rowTwo = _buildHeader(fnList, numArgs, pageName)
    outputList = [rowOne, rowTwo, ] + outputList
    
    outputTxt = "\n".join([",".join(row) for row in outputList])
    
    outputFN = join(outputPath, pageName + ".csv")
    codecs.open(outputFN, "wU", encoding="utf-8").write(outputTxt)
