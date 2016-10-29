'''
Created on Aug 11, 2015

@author: tmahrt
'''

import os
from os.path import join
import codecs

from lmeds.io import loader
from lmeds.io import user_response
from lmeds.post_process import transpose_utils
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
            elif taskName in ["prominence", "syllable_marking"]:
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
    
    aspectKeyList = returnDict[list(returnDict.keys())[0]].keys()
            
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
    with open(join(scorePath, "%s.csv" % stimulusID), "w") as fd:
        fd.write("\n".join([str(val) for val in sumList]))
    
    scorePath = join(featPath, scoreTxt + "_judgements")
    utils.makeDir(scorePath)
    with open(join(scorePath, "%s.csv" % stimulusID), "w") as fd:
        fd.write("\n".join([",".join(val) for val in
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


def _buildHeader(fnList, aspectKeyList, pageName, doSequenceOrder):
    # Build the name lists, which will take up the first two rows in the
    # spreadsheet.  One is normal, and one is anonymized
    oom = utils.orderOfMagnitude(len(fnList))
    userNameTemplate = "t%%0%dd" % (oom + 1) + ".%s%%s"
    
    bNameList = [os.path.splitext(name)[0] + ".b%s" for name in fnList]
    anonBNameList = [userNameTemplate % (i + 1, 'b')
                     for i in range(len(fnList))]
    
    pNameList = [os.path.splitext(name)[0] + ".p%s" for name in fnList]
    anonPNameList = [userNameTemplate % (i + 1, 'p')
                     for i in range(len(fnList))]
    headerDict = {"boundary": (bNameList, anonBNameList),
                  "prominence": (pNameList, anonPNameList),
                  "syllable_marking": (pNameList, anonPNameList),
                  "boundary_and_prominence": (bNameList + pNameList,
                                              anonBNameList + anonPNameList)}
    
    aspectInitialsDict = _getSmallestPrefix(aspectKeyList)
    
    bTxt = "sum.b%(aspect)s"
    pTxt = "sum.p%(aspect)s"
    
    txtPrefixDict = {"boundary": (bTxt),
                     "prominence": (pTxt),
                     "syllable_marking": (pTxt),
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
    
    # Add the sequence order if needed
    if doSequenceOrder:
        txtPrefixDict2 = {"boundary": "b%(aspect)s",
                          "prominence": "p%(aspect)s",
                          "syllable_marking": "p%(aspect)s",
                          "boundary_and_prominence": "bp%(aspect)s"}
        sequencePageCode = txtPrefixDict2[pageName] % {'aspect': aspectInitial}
        tmpTuple = transpose_utils.getUserSeqHeader(fnList,
                                                    sequencePageCode,
                                                    oom)
        seqHeader, anonSeqHeader = tmpTuple
        headerRow += "," + ",".join(seqHeader)
        anonHeaderRow += "," + ",".join(anonSeqHeader)
    
    return headerRow, anonHeaderRow


def _unifyRow(row):
    return [",".join(cells) if isinstance(cells, list) else cells
            for cells in row]


def _getDemarcator(argList):
    syllableDemarcator = None
    for arg in argList:
        if "syllableDemarcator" in arg:
            syllableDemarcator = arg.split("=")[1]
            
    return syllableDemarcator
        
        
def transposeRPT(path, txtPath, pageName, outputPath):
    '''
    Transposes RPT data
    
    Input files: one file per subject
    Output files: one file per stimuli
    '''
    utils.makeDir(outputPath)

    # Load response data
    responseDataList = []
    fnList = utils.findFiles(path, filterExt=".csv")
    for fn in fnList:
        a = user_response.loadUserResponse(join(path, fn))
        responseDataList.append(a)
    
    # Load the demarcator, if there is one
    # and load the order info if present
    demarcator = None
    pageName, pageArgs, _, _ = responseDataList[0][0]
    if pageName == "syllable_marking":
        
        # The demarcator can either be an arg or a keyword arg.
        # Either way, it should be the last item in the list
        demarcator = pageArgs[-1]
        if "syllableDemarcator" in demarcator:
            demarcator = demarcator.split("=")[1]
    
    # Sort response if sequence order information is available
    parsedTuple = transpose_utils.parseResponse(responseDataList)
    responseDataList, _, orderListOfLists = parsedTuple
    orderList = []
    if len(orderListOfLists) > 0:
        orderList = [",".join(row) for row
                     in utils.safeZip(orderListOfLists, True)]
    
    # Load Words
    txtDict = {}
    for fn in utils.findFiles(txtPath, filterExt=".txt"):
        name = os.path.splitext(fn)[0]
        txtList = loader.loadTxtFile(join(txtPath, fn))
        
        txtList = [tmpTxt.replace(" ", ",") for tmpTxt in txtList]
        
        # Remove HTML tags
        txtList = [word for word in txtList if "<" not in word]
        
        txt = ",".join(txtList)
        
        if demarcator is None:
            txtDict[name] = [word for word in txt.split(",") if word != ""]
        else:
            txtDict[name] = [syllable for word in txt.split(",") if word != ""
                             for syllable in word.split(demarcator)]
    
    returnDict, idKeyList, aspectKeyList = _transposeRPT(responseDataList)
    
    doUserSeqHeader = len(orderListOfLists) > 0
    headerRow, anonHeaderRow = _buildHeader(fnList, aspectKeyList, pageName,
                                            doUserSeqHeader)
    
    # Format the output rpt scores
    aggrOutputList = [headerRow, anonHeaderRow]
    for i in range(len(idKeyList)):
        
        stimulusID = idKeyList[i]
        
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
            elif pageName in ["prominence", "syllable_marking"]:
                aspectSumList.extend([pSumList, ])
                aspectList.extend([pScoreList, ])
            elif pageName == "boundary_and_prominence":
                aspectSumList.extend([bSumList, pSumList, ])
                aspectList.extend([bScoreList, pScoreList, ])
        
            # Extend header with sequence order information
            if doUserSeqHeader:
                orderStr = orderList[i]
                numAnnotators = range(max([len(bSumList), len(pSumList)]))
                tmpOrderList = [orderStr for _ in numAnnotators]
                aspectList.extend([tmpOrderList, ])
            
        dataList = aspectSumList + aspectList
        combinedList = [_unifyRow(row) for row in
                        utils.safeZip(dataList, enforceLength=True)]
        aggrOutputList.extend([",".join(row) for row in combinedList])
        
    outputTxt = "\n".join(aggrOutputList)
    
    outputFN = join(outputPath, pageName + ".csv")
    with codecs.open(outputFN, "w", encoding="utf-8") as fd:
        fd.write(outputTxt)
