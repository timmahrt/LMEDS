'''
Created on Aug 11, 2015

@author: tmahrt
'''

import os
from os.path import join
import io

from lmeds.lmeds_io import survey
from lmeds.lmeds_io import user_response
from lmeds.utilities import utils


def transposeSurvey(path, surveyFullPathList, outputPath):
    utils.makeDir(outputPath)
    
    surveyDataList = []
    fnList = utils.findFiles(path, filterExt=".csv")
    for fn in fnList:
        surveyDataList.append(user_response.loadUserResponse(join(path, fn)))
    
    aspectKeyList = []
    
    # Load the data
    returnDict = {}
   
    defaultDict = {}
    for surveyFN in surveyFullPathList:
        fn = os.path.split(surveyFN)[1]
        surveyName = os.path.splitext(fn)[0]
        
        questionTitleDataList = []
        surveyQuestionDataList = []
        surveyItemList = survey.parseSurveyFile(surveyFN)
        for surveyItem in surveyItemList:
            for widgetType, widgetTextList in surveyItem.widgetList:
                if widgetType == "None":
                    continue
                if widgetType in ["Multiline_Textbox", "Sliding_Scale"]:
                    widgetTextList = ["", ]
                blankTxt = ["", ] * (len(widgetTextList) - 1)
                # Removing commas b/c we're using csv files
                surveyQuestion = surveyItem.text.replace(",", "")
                questionTitleDataList.extend([surveyQuestion, ] + blankTxt)
                if len(widgetTextList) == 0:
                    surveyQuestionDataList.extend(["", ])
                else:
                    surveyQuestionDataList.extend(widgetTextList)
        
        defaultDict.setdefault(surveyName, [])
        defaultDict[surveyName].append(questionTitleDataList)
        defaultDict[surveyName].append(surveyQuestionDataList)
    
    for fn, userDataList in utils.safeZip([fnList, surveyDataList], True):
        
        for dataTuple in userDataList:
            # taskName, stimuliArgList, argTxt, dataTxt = dataTuple
            stimuliArgList = dataTuple[1]
            stimuliID = stimuliArgList[0]
            dataTxt = dataTuple[3]
            
            returnDict.setdefault(stimuliID, defaultDict[stimuliID])
            
            dataList = dataTxt.split(",")
            returnDict[stimuliID].append(dataList)
    
    idKeyList = returnDict.keys()
    
    # Transpose the data
    for stimulusID in idKeyList:
        returnDict[stimulusID] = [list(subTuple) for subTuple in
                                  utils.safeZip(returnDict[stimulusID],
                                                enforceLength=True)]
        
        # Add a summation column
        newData = []
        for row in returnDict[stimulusID]:
            
            try:
                total = str(sum([int(val) if val != '' else 0
                                 for val in row[2:]]))
            except ValueError:
                total = '-'
            newData.append(row[:2] + [total, ] + row[2:])
        returnDict[stimulusID] = newData
        
        mainSurveyData = [",".join(subList) for subList in
                          returnDict[stimulusID]]
        
        outputTxtList = [",".join(["", "", "Total", ] + fnList), ]
        outputTxtList += mainSurveyData
        
        outputTxt = "\n".join(outputTxtList)
        outputFN = join(outputPath, stimulusID + ".csv")
        with io.open(outputFN, "w", encoding="utf-8") as fd:
            fd.write(outputTxt)
            
    return returnDict, idKeyList, aspectKeyList
