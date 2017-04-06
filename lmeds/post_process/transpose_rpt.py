'''
Created on Aug 11, 2015

@author: tmahrt
'''

import os
from os.path import join
import io
import copy

from lmeds.lmeds_io import loader
from lmeds.lmeds_io import user_response
from lmeds.post_process import transpose_utils
from lmeds.utilities import utils

P = "p"
B = "b"


def _transposeRPT(dataListOfLists):

    idKeyList = []
    
    # Load the data
    returnDict = {}
    bCountList = []
    pCountList = []
    j = -1
    for dataList in dataListOfLists:
        j += 1
        bCountList.append([])
        pCountList.append([])
        
        oom = utils.orderOfMagnitude(len(dataList)) + 1
        stimTemplate = "s_%%0%dd," % oom
        i = 0
        for taskName, stimuliArgList, _, dataTxt in dataList:
            i += 1
            
            # Remove the sequence order variables from the stimuli arg list
            omitList = []
            for stimuliI, arg in enumerate(stimuliArgList):
                if 'orderSI=' in arg:
                    omitList.append(stimuliI)
                    continue
                if 'orderAI=' in arg:
                    omitList.append(stimuliI)
                    continue
            omitList.reverse()
            
            cutStimuliArgList = copy.deepcopy(stimuliArgList)
            for argI in omitList:
                cutStimuliArgList.pop(argI)
            
            stimuliID = stimTemplate % i + ','.join(cutStimuliArgList)
            
#             tmpAspectListToCount.append(aspect)
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
            else:
                bScores = None
                pScores = None
            
            pCountList[-1].append(len(pScores))
            bCountList[-1].append(len(bScores))
            
            if j == 0:
                idKeyList.append(stimuliID)
            
            returnDict.setdefault(stimuliID, {})
            returnDict[stimuliID].setdefault(B, [])
            returnDict[stimuliID].setdefault(P, [])
            
            returnDict[stimuliID][B].append(bScores)
            returnDict[stimuliID][P].append(pScores)
            
    # Transpose the data
    for sid in idKeyList:
        for taskType in [B, P]:
            try:
                tmpList = returnDict[sid][taskType]
            except KeyError:
                continue
            if len(tmpList) == 0:
                continue
            try:
                zipped = utils.safeZip(tmpList,
                                       enforceLength=True)
            except:
                print("Problem with score type: %s, SID: %s" % (taskType, sid))
                raise
            returnDict[sid][taskType] = [list(subTuple)
                                         for subTuple in zipped]
        
    return returnDict, idKeyList


def _getScores(userData, scoreType):
    scoreList = userData[scoreType]
    
    # HACK to accommodate bug in output code
    scoreList = [row for row in scoreList
                 if all([item != '' for item in row])]
    
    sumList = ["%.03f" % (sum([float(val) for val in subList]) / len(subList))
               for subList in scoreList]
    
    return scoreList, sumList


def _outputScores(featPath, aspect, stimulusID, returnDict,
                  sumList, scoreType):
    
    scoreTxt = "%s_%sscores" % (aspect, scoreType.lower())
    scorePath = join(featPath, scoreTxt)
    utils.makeDir(scorePath)
    fn = join(scorePath, "%s.csv" % stimulusID)
    with io.open(fn, "w", encoding="utf-8") as fd:
        fd.write("\n".join([str(val) for val in sumList]))
    
    scorePath = join(featPath, scoreTxt + "_judgements")
    utils.makeDir(scorePath)
    fn = join(scorePath, "%s.csv" % stimulusID)
    with io.open(fn, "w", encoding="utf-8") as fd:
        fd.write("\n".join([",".join(val) for val in
                            returnDict[stimulusID][scoreType]]))


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


def _buildHeader(fnList, pageName, doSequenceOrder, sampleHeader):
    # Build the name lists, which will take up the first two rows in the
    # spreadsheet.  One is normal, and one is anonymized
    oom = utils.orderOfMagnitude(len(fnList))
    userNameTemplate = "t%%0%dd" % (oom + 1) + ".%s"
    
    bNameList = [os.path.splitext(name)[0] + ".b" for name in fnList]
    anonBNameList = [userNameTemplate % (i + 1, 'b')
                     for i in range(len(fnList))]
    
    pNameList = [os.path.splitext(name)[0] + ".p" for name in fnList]
    anonPNameList = [userNameTemplate % (i + 1, 'p')
                     for i in range(len(fnList))]
    headerDict = {"boundary": (bNameList, anonBNameList),
                  "prominence": (pNameList, anonPNameList),
                  "syllable_marking": (pNameList, anonPNameList),
                  "boundary_and_prominence": (bNameList + pNameList,
                                              anonBNameList + anonPNameList)}
    
    bTxt = "sum.b"
    pTxt = "sum.p"
    
    txtPrefixDict = {"boundary": (bTxt),
                     "prominence": (pTxt),
                     "syllable_marking": (pTxt),
                     "boundary_and_prominence": ("%s,%s" % (bTxt, pTxt))}
    
    nameList, anonNameList = headerDict[pageName]
    header2Prefix = txtPrefixDict[pageName]
    
    sumHeaderList = []
    headerList = []
    anonHeaderList = []
    sumHeaderList.append(header2Prefix)
    headerList.extend([name
                       for name in nameList])
    anonHeaderList.extend([name
                           for name in anonNameList])
    
    sumTxt = ",".join(sumHeaderList)
    headerStr = ",".join(headerList)
    anonHeaderStr = ",".join(anonHeaderList)
    
    commaStr = "," * (sampleHeader.count(",") - 1)
    rowTemplate = "StimulusID," + commaStr + ",Word,%s,%s"

    headerRow = rowTemplate % (sumTxt, headerStr)
    anonHeaderRow = rowTemplate % (sumTxt, anonHeaderStr)
    
    # Add the sequence order if needed
    if doSequenceOrder:
        txtPrefixDict2 = {"boundary": "b",
                          "prominence": "p",
                          "syllable_marking": "p",
                          "boundary_and_prominence": "bp"}
        sequencePageCode = txtPrefixDict2[pageName]
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
    
    returnDict, idKeyList = _transposeRPT(responseDataList)
    
    doUserSeqHeader = len(orderListOfLists) > 0
    headerRow, anonHeaderRow = _buildHeader(fnList, pageName,
                                            doUserSeqHeader,
                                            idKeyList[0])
    
    # Format the output rpt scores
    aggrOutputList = [headerRow, anonHeaderRow]
    for i in range(len(idKeyList)):
        
        stimulusID = idKeyList[i]

        wordList = txtDict[stimulusID.split(",")[2]]
        stimulusIDList = [stimulusID for _ in wordList]
        aspectSumList = [stimulusIDList, wordList, ]
        aspectList = []

        try:
            bScoreList, bSumList = _getScores(returnDict[stimulusID],
                                              B)
        except KeyError:
            pass
        try:
            pScoreList, pSumList = _getScores(returnDict[stimulusID],
                                              P)
        except KeyError:
            pass
        
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
    with io.open(outputFN, "w", encoding="utf-8") as fd:
        fd.write(outputTxt)
