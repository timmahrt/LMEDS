'''
Created on Aug 21, 2015

@author: tmahrt


transpose_choice.py has some unique code.  This code is run by
user_scripts/post_process_results.py

Unlike other transpose page post-processing script, this code
also includes functionality that requires more user input.  Specifically,
it has functions for generating the results files and checking whether
user's responses are correct or not and generating a confusion matrix of
the results.  Here is one simple example


# Suppose we ran an experiment with abn pages.  Each stimuli was either
# of category A or B and marked as such on file name.  Users select
# 0 if they hear category A or 1 if they hear category B.
# -start by running user_scripts/post_process_results.py to get transposed data
# -then:

from os.path import join

def myFunc(inputList):
    # Each cell in inputList is one cell in a row of the output of
    # post_process_results.py (abn.csv)
    if 'A' in inputList[1]:
        returnVal = "0"
    elif "B" in inputList[1]:
        returnVal = "1"
    
    return returnVal

dataPath = "location/to/duplicates_removed_results"
originalFN = join(dataPath, "abn.csv")
correctionFN = join(dataPath, "abn_answer_template.csv")
correctAnswersFN = join(dataPath, "abn_answers.csv")
correctedFN = join(dataPath, "abn_corrected.csv")

# This outputs > abn_answers.csv
transpose_choice.generateCorrectResponse(correctionFN, myFunc,
                                         correctAnswersFN)
   
# This outputs > abn_corrected.csv and abn_corrected_confusion_matrix.csv
transpose_choice.markCorrect(originalFN, correctAnswersFN,
                             correctedFN)

'''

import os
from os.path import join
import io

from lmeds.lmeds_io import sequence
from lmeds.lmeds_io import user_response
from lmeds.post_process import transpose_utils
from lmeds.utilities import utils


def _buildHeader(fnList, numArgs, pageName, doSequenceOrder):
    # Build the name lists, which will take up the first two rows in the
    # spreadsheet.  One is normal, and one is anonymized
    oom = utils.orderOfMagnitude(len(fnList))
    userNameTemplate = "t%%0%dd.%s" % (oom + 1, pageName)
    nameList = [os.path.splitext(name)[0] + "." + pageName for name in fnList]
    anonNameList = [userNameTemplate % (i + 1)
                    for i in range(len(fnList))]
    
    headerPrefixList = ["stimulusID", ]
    headerPrefixList += ["arg%d" % (i + 1) for i in range(numArgs)]
    
    nameList = headerPrefixList + nameList
    anonNameList = headerPrefixList + anonNameList
    
    if doSequenceOrder:
        tmpTuple = transpose_utils.getUserSeqHeader(fnList, pageName, oom)
        seqHeader, anonSeqHeader = tmpTuple
        nameList += seqHeader
        anonNameList += anonSeqHeader
    
    return nameList, anonNameList


def _parseTransposed(inputFN, isAnswerFlag):
    
    with io.open(inputFN, "r", encoding="utf-8") as fd:
        dataList = fd.readlines()
    dataList = [sequence.recChunkLine(row, ",") for row in dataList]
    
    header = None
    headerList = []
    while True:
        if dataList[0][0] == "stimulusID":
            header = dataList.pop(0)
            headerList.append(header)
        else:
            break
            
    if header is not None:
        i = 1
        while True:
            if 'arg' in header[i]:
                i += 1
            else:
                i -= 1
                break
        i += 1
    
    if isAnswerFlag:
        returnList = [(row[:-1], row[-1]) for row in dataList]
    else:
        returnList = [(row[:i], row[i:]) for row in dataList]
    
    return headerList, returnList


def _generateConfusionMatrix(correctList, responseList, percentFlag):
    
    # Initialize dictionary
    confusionDict = {}
    flattenedResponseList = [val for sublist in responseList
                             for val in sublist]
    keyList = list(set(flattenedResponseList + correctList))
    keyList.sort()
    sumDict = {}
    for key1 in keyList:
        confusionDict[key1] = {}
        for key2 in keyList:
            confusionDict[key1][key2] = 0
            sumDict[key1] = 0
    
    # Sum values
    for answer, responses in utils.safeZip([correctList, responseList], True):
        for response in responses:
            confusionDict[answer][response] += 1
            sumDict[answer] += 1
    
    # Generate confusion matrix
    outputList = [["", ] + keyList, ]
    for key1 in keyList:
        subList = [key1, ]
        for key2 in keyList:
            
            value = confusionDict[key1][key2]
            if percentFlag:
                try:
                    value = value / float(sumDict[key1])
                except ZeroDivisionError:
                    value = 0
            value = "%0.2f" % (value)
            
            subList.append(value)
        outputList.append(subList)
    
    return outputList


def transposeChoice(path, pageName, outputPath):
    
    utils.makeDir(outputPath)
    
    # Load response data
    responseDataList = []
    fnList = utils.findFiles(path, filterExt=".csv")
    for fn in fnList:
        a = user_response.loadUserResponse(join(path, fn))
        responseDataList.append(a)
    
    # Sort response if sequence order information is available
    parsedTuple = transpose_utils.parseResponse(responseDataList)
    responseDataList, stimuliListsOfLists, orderListOfLists = parsedTuple
    
    # Convert response to single answer
    tmpUserResponse = []
    for userDataList in responseDataList:
        # Get user response
        userResponse = [str(responseTuple[3].split(',').index('1'))
                        for responseTuple in userDataList]
        tmpUserResponse.append(userResponse)
    
    responseDataList = tmpUserResponse

    # Verify that all responses have the same list of stimuli
    assert(all([stimuliListsOfLists[0] == header
                for header in stimuliListsOfLists]))
    
    # Transpose data
    tResponseDataList = [row for row in utils.safeZip(responseDataList, True)]
    tOrderListOfLists = []
    if len(orderListOfLists) > 0:
        tOrderListOfLists = [row for row
                             in utils.safeZip(orderListOfLists, True)]
    
    # Add a unique id to each row
    oom = utils.orderOfMagnitude(len(stimuliListsOfLists[0]))
    stimID = "s%%0%dd" % (oom + 1)
    stimuliList = ["%s,%s" % (stimID % i, row)
                   for i, row in enumerate(stimuliListsOfLists[0])]
    
    addSequenceInfo = len(tOrderListOfLists) > 0
    if addSequenceInfo:  # Add sequence information to each row
        tResponseDataList = [list(row) + list(sequenceInfo)
                             for row, sequenceInfo
                             in utils.safeZip([tResponseDataList,
                                               tOrderListOfLists], True)]

    # Aggregate the stimuli and the responses in rows
    tResponseDataList = [list(row)
                         for row
                         in tResponseDataList]
    outputList = [[header, ] + list(row)
                  for header, row
                  in utils.safeZip([stimuliList, tResponseDataList], True)]
    
    # Add the column heading rows
    # First row in unanonymized user names; Second row is anonymized
    numArgs = stimuliList[0].count(",")
    rowOne, rowTwo = _buildHeader(fnList, numArgs, pageName, addSequenceInfo)
    outputList = [rowOne, rowTwo, ] + outputList
    
    outputTxt = u"\n".join([",".join(row) for row in outputList])
    outputFN = join(outputPath, pageName + ".csv")
    with io.open(outputFN, "w", encoding="utf-8") as fd:
        fd.write(outputTxt)

    # Output a template users can fill in to auto score the results
    name = pageName + "_answer_template.csv"
    answersFN = join(outputPath, name)
    if os.path.exists(answersFN):
        print("Response template '%s' already exists.  Not overwriting."
              % name)
    else:
        outputTxt = u"\n".join(stimuliList)
        with io.open(answersFN, "w", encoding="utf-8") as fd:
            fd.write(outputTxt)


def generateCorrectResponse(correctionFN, ruleFunc, outputFN):
    '''
    Generate the correct answer based on some critera
    
    /ruleFunc/ takes a list of arguments (one element for each cell in a row
    of the input) and outputs a decision, which is added to the row
    '''
    with io.open(correctionFN, "r", encoding="utf-8") as fd:
        dataList = fd.readlines()
    dataList = [row.strip() for row in dataList if len(row) > 0]
    
    outputList = []
    for row in dataList:
        cellList = sequence.recChunkLine(row, ",")
        decision = ruleFunc(cellList)
        outputList.append("%s,%s" % (row, decision))
    
    outputTxt = "\n".join(outputList)
    with io.open(outputFN, "w", encoding="utf-8") as fd:
        fd.write(outputTxt)
    

def markCorrect(inputFN, correctionFN, outputFN, evalFunc=None):
    '''
    Converts user responses into a binary--right or wrong--answer
    '''
    
    if evalFunc is None:
        evalFunc = lambda x, y: x == y
    
    # Load
    headerList, responseList = _parseTransposed(inputFN, False)
    answerList = _parseTransposed(correctionFN, True)[1]

    markedList = headerList
    for responseTuple, answerTuple in utils.safeZip([responseList, answerList],
                                                    True):
        assert(responseTuple[0] == answerTuple[0])
        
        userResponses = responseTuple[1]
        answer = answerTuple[1]
        markedRow = ["1" if evalFunc(val, answer) else "0"
                     for val in userResponses]
        
        markedList.append(responseTuple[0] + markedRow)
    
    markedList = [",".join([transpose_utils.recListToStr(item)
                            for item in row])
                  for row in markedList]
    outputTxt = "\n".join(markedList)
    with io.open(outputFN, "w", encoding="utf-8") as fd:
        fd.write(outputTxt)

    # Generate confusion matrix
    responseValList = [rTuple[1] for rTuple in responseList]
    answerValList = [aTuple[1] for aTuple in answerList]
    confusionMatrix = _generateConfusionMatrix(answerValList, responseValList,
                                               False)
    percentConfusionMatrix = _generateConfusionMatrix(answerValList,
                                                      responseValList,
                                                      True)
    
    confusionMatrix = confusionMatrix + ["", ] + percentConfusionMatrix
    
    matrixOutputFN = os.path.splitext(outputFN)[0] + "_confusion_matrix.csv"
    confusionMatrix = [",".join(row) for row in confusionMatrix]
    outputTxt = "\n".join(confusionMatrix)
    with io.open(matrixOutputFN, "w", encoding="utf-8") as fd:
        fd.write(outputTxt)
