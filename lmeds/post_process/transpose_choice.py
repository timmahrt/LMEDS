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
import codecs

from lmeds.io import sequence
from lmeds.io import user_response
from lmeds.utilities import utils


def _buildHeader(fnList, numArgs, pageName):
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
    
    return nameList, anonNameList


def _parseTransposed(inputFN, isAnswerFlag):
    
    dataList = codecs.open(inputFN, "r", encoding="utf-8").readlines()
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


def _recListToStr(someObj):
    if isinstance(someObj, list):
        tmpList = []
        for subVal in someObj:
            tmpList.append(_recListToStr(subVal))
        retStr = "[%s]" % " ".join(tmpList)
    else:
        retStr = str(someObj)
    
    return retStr


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
        
        userStimuli = []
        for responseTuple in userDataList:
            rowData = [_recListToStr(row) for row in responseTuple[1]]
            userStimuli.append(",".join(rowData))
        
        if stimuliList == []:
            stimuliList = userStimuli
        stimuliListsOfLists.append(userStimuli)
    
    # Assert all the headers are the same for each user
    assert(all([stimuliListsOfLists[0] == header
                for header in stimuliListsOfLists]))
    
    # Transpose data
    tResponseDataList = [row for row in utils.safeZip(responseDataList, True)]
    
    # Add a unique id to each row
    oom = utils.orderOfMagnitude(len(stimuliList))
    stimID = "s%%0%dd" % (oom + 1)
    stimuliList = ["%s,%s" % (stimID % i, row)
                   for i, row in enumerate(stimuliList)]
    
    # Add stimuli information to each row
    outputList = [[header, ] + list(row) for header, row
                  in utils.safeZip([stimuliList, tResponseDataList], True)]
    
    # Add the column heading rows
    # First row in unanonymized user names
    # Second row is anonymized
    numArgs = stimuliList[0].count(",")
    rowOne, rowTwo = _buildHeader(fnList, numArgs, pageName)
    outputList = [rowOne, rowTwo, ] + outputList
    
    outputTxt = "\n".join([",".join(row) for row in outputList])
    
    outputFN = join(outputPath, pageName + ".csv")
    codecs.open(outputFN, "wU", encoding="utf-8").write(outputTxt)

    # Output a template users can fill in to auto score the results
    name = pageName + "_answer_template.csv"
    answersFN = join(outputPath, name)
    if os.path.exists(answersFN):
        print("Response template '%s' already exists.  Not overwriting."
              % name)
    else:
        outputTxt = "\n".join(stimuliList)
        codecs.open(answersFN, "wU", encoding="utf-8").write(outputTxt)


def generateCorrectResponse(correctionFN, ruleFunc, outputFN):
    '''
    Generate the correct answer based on some critera
    
    /ruleFunc/ takes a list of arguments (one element for each cell in a row
    of the input) and outputs a decision, which is added to the row
    '''
    dataList = codecs.open(correctionFN, "r", encoding="utf-8").readlines()
    dataList = [row.strip() for row in dataList if len(row) > 0]
    
    outputList = []
    for row in dataList:
        cellList = sequence.recChunkLine(row, ",")
        decision = ruleFunc(cellList)
        outputList.append("%s,%s" % (row, decision))
    
    outputTxt = "\n".join(outputList)
    codecs.open(outputFN, "w", encoding="utf-8").write(outputTxt)
    

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
    
    markedList = [",".join([_recListToStr(item) for item in row])
                  for row in markedList]
    outputTxt = "\n".join(markedList)
    codecs.open(outputFN, "w", encoding="utf-8").write(outputTxt)

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
    codecs.open(matrixOutputFN, "w", encoding="utf-8").write(outputTxt)
