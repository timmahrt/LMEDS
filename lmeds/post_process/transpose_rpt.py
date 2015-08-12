'''
Created on Aug 11, 2015

@author: tmahrt
'''

import os
from os.path import join
import codecs

from lmeds.io import loader
from lmeds.io import user_response
from lmeds.utilities import utils

P = "p"
B = "b"


def _transposeRPT(dataListOfLists):

    idKeyList = []
    aspectKeyList = []
    
    # Load the data
    returnDict = {}
    bCountList = []
    pCountList = []
    for dataList in dataListOfLists:
        bCountList.append([])
        pCountList.append([])
        
        tmpAspectListToCount = []
        for taskName, stimuliArgList, _, dataTxt in dataList:
            stimuliID = stimuliArgList[0]
            aspect = stimuliArgList[4]
            
            tmpAspectListToCount.append(aspect)
            dataList = dataTxt.split(",")
            
            if taskName == 'boundary_and_prominence':
                lenOfData = int(len(dataList) / 2.0)
            
                bScores = dataList[:lenOfData]
                pScores = dataList[lenOfData:]
            elif taskName == "boundary":
                bScores = dataList
                pScores = []
            elif taskName == "prominence":
                bScores = []
                pScores = dataList
            
            pCountList[-1].append(len(pScores))
            bCountList[-1].append(len(bScores))
            
            idKeyList.append(stimuliID)
            aspectKeyList.append(aspect)
            
            returnDict.setdefault(stimuliID, {})
            returnDict[stimuliID].setdefault(aspect, {})
            returnDict[stimuliID][aspect].setdefault(B, [])
            returnDict[stimuliID][aspect].setdefault(P, [])
            
            returnDict[stimuliID][aspect][B].append(bScores)
            returnDict[stimuliID][aspect][P].append(pScores)
            
    idKeyList = list(set(idKeyList))
    idKeyList.sort()
    
    aspectKeyList = returnDict[returnDict.keys()[0]].keys()
            
    # Transpose the data
    for sid in idKeyList:
        for aspect in aspectKeyList:
            for taskType in [B, P]:
                zipped = utils.safeZip(returnDict[sid][aspect][taskType],
                                       enforceLength=True)
                returnDict[sid][aspect][taskType] = [list(subTuple)
                                                     for subTuple in zipped]
        
    return returnDict, idKeyList, aspectKeyList


def _getScores(userData, scoreType):
    scoreList = userData[scoreType]
    
    # HACK to accommodate bug in output code
    scoreList = [row for row in scoreList
                 if all([item != '' for item in row])]
    
    sumList = ["%.03f" % (sum([float(val) for val in subList]) / len(subList))
               for subList in scoreList]
#     scoreList = [lst + ["%.03f" % sumVal, ]
#                  for lst, sumVal in zip(scoreList, sumList)]
    
    return scoreList, sumList


def _outputScores(featPath, aspect, stimulusID, returnDict,
                  sumList, scoreType):
    
    scoreTxt = "%s_%sscores" % (aspect, scoreType.lower())
    scorePath = join(featPath, scoreTxt)
    utils.makeDir(scorePath)
    open(join(scorePath, "%s.csv" % stimulusID),
         "w").write("\n".join([str(val) for val in sumList]))
    
    scorePath = join(featPath, scoreTxt + "_judgements")
    utils.makeDir(scorePath)
    open(join(scorePath, "%s.csv" % stimulusID),
         "w").write("\n".join([",".join(val) for val in
                               returnDict[stimulusID][aspect][scoreType]]))


def _getSmallestPrefix(keywordList):
    wordPrefixDict = {}
    lenList = [len(word) for word in keywordList]
    minLen = min(lenList)
    i = 1
    while i < minLen:
        prefixList = [word[:i] for word in keywordList]
        if all([prefixList.count(prefix) == 1 for prefix in prefixList]):
            for word, prefix in zip(keywordList, prefixList):
                wordPrefixDict[word] = prefix
            break
        else:
            i += 1
            
    return wordPrefixDict


def _buildHeader(fnList, aspectKeyList, pageName):
    # Build the name lists, which will take up the first two rows in the
    # spreadsheet.  One is normal, and one is anonymized
    oom = utils.orderOfMagnitude(len(fnList))
    userNameTemplate = "t%%0%dd" % (oom + 1) + ".%s%%s"
    
    bNameList = [os.path.splitext(name)[0] + ".b%s" for name in fnList]
    anonBNameList = [userNameTemplate % (i + 1, 'b')
                     for i in xrange(len(fnList))]
    
    pNameList = [os.path.splitext(name)[0] + ".p%s" for name in fnList]
    anonPNameList = [userNameTemplate % (i + 1, 'p')
                     for i in xrange(len(fnList))]
    headerDict = {"boundary": (bNameList, anonBNameList),
                  "prominence": (pNameList, anonPNameList),
                  "boundary_and_prominence": (bNameList + pNameList,
                                              anonBNameList + anonPNameList)}
    
    aspectInitialsDict = _getSmallestPrefix(aspectKeyList)
    
    bTxt = "sum.b%(aspect)s"
    pTxt = "sum.b%(aspect)s"
    
    txtPrefixDict = {"boundary": (bTxt),
                     "prominence": (pTxt),
                     "boundary_and_prominence": ("%s,%s" % (bTxt, pTxt))}
    
    nameList, anonNameList = headerDict[pageName]
    header2Prefix = txtPrefixDict[pageName]
    
    sumHeaderList = []
    headerList = []
    anonHeaderList = []
    for aspect in aspectKeyList:
        aspectInitial = aspectInitialsDict[aspect]
        sumHeaderList.append(header2Prefix % {'aspect': aspectInitial})
        headerList.extend([name % aspectInitial
                           for name in nameList])
        anonHeaderList.extend([name % aspectInitial
                               for name in anonNameList])
    
    sumTxt = ",".join(sumHeaderList)
    headerStr = ",".join(headerList)
    anonHeaderStr = ",".join(anonHeaderList)
    
    rowTemplate = "StimulusID,Word,%s,%s"

    headerRow = rowTemplate % (sumTxt, headerStr)
    anonHeaderRow = rowTemplate % (sumTxt, anonHeaderStr)
    return headerRow, anonHeaderRow


def _unifyRow(row):
    return [",".join(cells) if isinstance(cells, list) else cells
            for cells in row]


def transposeRPT(path, txtPath, pageName, outputPath):
    '''
    Transposes RPT data
    
    Input files: one file per subject
    Output files: one file per stimuli
    '''
    utils.makeDir(outputPath)
    
    # Load Words
    txtDict = {}
    for fn in utils.findFiles(txtPath, filterExt=".txt"):
        name = os.path.splitext(fn)[0]
        txtList = loader.loadTxtFile(join(txtPath, fn))
        
        txtList = [tmpTxt.replace(" ", ",") for tmpTxt in txtList]
        
        # Remove HTML tags
        txtList = [word for word in txtList if "<" not in word]
        
        txt = ",".join(txtList)
        
        txtDict[name] = [word for word in txt.split(",") if word != ""]
        
    # Load p/b-score data
    rptDataList = []
    fnList = utils.findFiles(path, filterExt=".csv")
    for fn in fnList:
        a = user_response.loadUserResponse(join(path, fn))
        rptDataList.append(a)
    
    returnDict, idKeyList, aspectKeyList = _transposeRPT(rptDataList)
    
    headerRow, anonHeaderRow = _buildHeader(fnList, aspectKeyList, pageName)
    
    aggrOutputList = [headerRow, anonHeaderRow]
    for stimulusID in idKeyList:
        wordList = txtDict[stimulusID]
        stimulusIDList = [stimulusID for _ in wordList]
        aspectSumList = [stimulusIDList, wordList, ]
        aspectList = []
        for aspect in aspectKeyList:
            bScoreList, bSumList = _getScores(returnDict[stimulusID][aspect],
                                              B)
            pScoreList, pSumList = _getScores(returnDict[stimulusID][aspect],
                                              P)
            if pageName == "boundary":
                aspectSumList.extend([bSumList, ])
                aspectList.extend([bScoreList, ])
            elif pageName == "prominence":
                aspectSumList.extend([pSumList, ])
                aspectList.extend([pScoreList, ])
            elif pageName == "boundary_and_prominence":
                aspectSumList.extend([bSumList, pSumList, ])
                aspectList.extend([bScoreList, pScoreList, ])
                
        dataList = aspectSumList + aspectList
        combinedList = [_unifyRow(row) for row in
                        utils.safeZip(dataList, enforceLength=True)]
        aggrOutputList.extend([",".join(row) for row in combinedList])
        
    outputTxt = "\n".join(aggrOutputList)
    
    outputFN = join(outputPath, pageName + ".csv")
    codecs.open(outputFN, "wU", encoding="utf-8").write(outputTxt)
