'''
Created on Oct 28, 2016

@author: Tim
'''

import os


def getUserSeqHeader(fnList, pageName, oom):
    
    userNameSeqTemplate = "t%%0%dd.%s.seq" % (oom + 1, pageName)
    
    nameSeqList = ["%s.%s.seq" % (os.path.splitext(name)[0], pageName)
                   for name in fnList]
    
    anonNameSeqList = [userNameSeqTemplate % (i + 1)
                       for i in range(len(fnList))]
    
    return nameSeqList, anonNameSeqList


def recListToStr(someObj):
    if isinstance(someObj, list):
        tmpList = []
        for subVal in someObj:
            tmpList.append(recListToStr(subVal))
        retStr = "[%s]" % " ".join(tmpList)
    else:
        retStr = str(someObj)
    
    return retStr


def parseOrderStr(rowStr):
    rowStr, tail = rowStr.split(',orderSI=')
    orderSI, orderAI = tail.split(',orderAI=')
    
    return rowStr, orderSI, orderAI


def parseResponse(userResponseList):

    # Convert response to single answer
    cleanedUserResponseList = []
    stimuliListsOfLists = []
    orderListOfLists = []

    orderStr = ',orderSI='

    for userDataList in userResponseList:
        
        # Get user stimuli
        userStimuli = []
        for responseTuple in userDataList:
            rowData = [recListToStr(row) for row in responseTuple[1]]
            userStimuli.append(",".join(rowData))
    
        # If necessary, arrange the user's stimuli in the order of the
        # original (unrandomized) sequence order
        # This also removes the order string from the user's response
        tmpOrderList = []
        if orderStr in userStimuli[0]:
            tmpStimList = []
            tmpRowList = []
            for i in range(len(userStimuli)):
                row = userStimuli[i]
                userData = userDataList[i]
                row, origI, actualI = parseOrderStr(row)
                origI = int(origI)
                tmpStimList.append((origI, row))
                tmpRowList.append((origI, userData))
                tmpOrderList.append((origI, actualI))
            
            tmpStimList.sort()
            tmpRowList.sort()
            tmpOrderList.sort()
            
            userStimuli = [row for _, row in tmpStimList]
            userDataList = [row for _, row in tmpRowList]
            tmpOrderList = [row for _, row in tmpOrderList]
            
        # The final output
        cleanedUserResponseList.append(userDataList)
        stimuliListsOfLists.append(userStimuli)
        
        if len(tmpOrderList) > 0:
            orderListOfLists.append(tmpOrderList)
    
    return cleanedUserResponseList, stimuliListsOfLists, orderListOfLists
