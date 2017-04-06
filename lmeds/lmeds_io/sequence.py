'''
Created on May 30, 2013

@author: timmahrt
'''

import os
from os.path import join
import io
import random

from lmeds.pages import factories


class TestSetupError(Exception):

    def __init__(self, unknownKeyList, *args, **kargs):
        super(TestSetupError, self).__init__(*args, **kargs)
        self.unknownKeyList = unknownKeyList

    def __str__(self):
        txtString = ("ERROR: The following keys were found in "
                     "'sequence.txt' but they are not associated with any "
                     "pages.  Please consult the test documentation or "
                     "the administrator."
                     )
        unknownKeyStr = "\n".join(self.unknownKeyList)
        
        txtString += "\n" + unknownKeyStr
        
        return txtString


class EndOfTestSequenceException(Exception):
    
    def __init__(self, sequenceFN):
        super(EndOfTestSequenceException, self).__init__()
        self.sequenceFN = sequenceFN
    
    def __str__(self):
        return "End of test sequence: '%s'" % self.sequenceFN


class InvalidFirstLine(Exception):
    
    def __init__(self, item):
        super(InvalidFirstLine, self).__init__()
        self.item = item
        
    def __str__(self):
        return ("ERROR: The first line in a sequence file must be "
                "the sequence title (i.e. start with '*').\n\nFound '%s."
                ) % self.item
    
    
class InvalidSequenceFileError(Exception):
    
    def __init__(self, item):
        super(InvalidSequenceFileError, self).__init__()
        self.item = item
        
    def __str__(self):
        return ("ERROR: The first command in a sequence file cannot be "
                "a subsequence (i.e. start with '#').\n\nFound '%s'."
                ) % self.item


class UnbalancedWrapperError(Exception):
    
    def __init__(self, text, startDelim, endDelim):
        super(UnbalancedWrapperError, self).__init__()
        self.text = text
        self.startDelim = startDelim
        self.endDelim = endDelim
    
    def __str__(self):
        return ("Unbalanced use of %s and %s in string \n %s"
                % (self.startDelim, self.endDelim, self.text))


class UserSequencePathError(Exception):
    
    def __init__(self, path):
        super(UserSequencePathError, self).__init__()
        self.path = path
        
    def __str__(self):
        return ("Path '%s' does not exist in test folder. "
                "Please create it and try again."
                % self.path)


def _createUserSequence(fromFN, toFN):
    title, sequenceList = parseSequence(fromFN, True)
    
    outputSequenceTxt = '*' + title + "\n"
    
    i = 0
    decrement = 0  # Don't count directives
    while i < len(sequenceList):
        if sequenceList[i] == "<randomize>":
            decrement += 1
            outputSequenceTxt += "\n"
            
            # Mark the original order of the stimuli,
            # so we can reconstruct it later
            subList = []
            i += 1
            j = 0
            while True:
                row = sequenceList[i + j]
                if row == "</randomize>":
                    break
                else:
                    subList.append((row, i - decrement + j))
                j += 1
                
            # Randomize order and mark the order this user did the sequence in
            random.shuffle(subList)
            for j, rowTuple in enumerate(subList):
                row, origI = rowTuple
                rowArgs = (row, origI, i - decrement + j)
                outputSequenceTxt += "%s orderSI=%d orderAI=%d\n" % rowArgs
            outputSequenceTxt += "\n"
            i += len(subList)
            
            # Extra 1 for </randomize> tag
            decrement += 1
            i += 1
        
        else:
            row = sequenceList[i]
            outputSequenceTxt += ("%s orderSI=%d orderAI=%d\n" %
                                  (row, i - decrement, i - decrement))
            i += 1
    
    with io.open(toFN, "w", encoding='utf-8') as fd:
        fd.write(outputSequenceTxt)


class TestSequence(object):
    
    def __init__(self, webSurvey, sequenceFN, individualSequenceName=None):

        if individualSequenceName is not None:
            sequencePath = os.path.split(sequenceFN)[0]
            
            # Loading the sequence title -- dropping the '*' prefix
            with io.open(sequenceFN, "r", encoding='utf-8') as fd:
                sequenceTitle = fd.readline().strip()[1:]
            
            newPath = join(sequencePath, "individual_sequences", sequenceTitle)
            
            if not os.path.exists(newPath):
                raise UserSequencePathError(join("<test_root>",
                                                 "individual_sequences",
                                                 sequenceTitle))
            
            newSequenceFN = join(newPath, individualSequenceName + ".txt")
            if not os.path.exists(newSequenceFN):
                _createUserSequence(sequenceFN, newSequenceFN)
            sequenceFN = newSequenceFN
        
        self.sequenceFN = sequenceFN
    
        self.webSurvey = webSurvey  # Needed to instantiate pages
        self.sequenceTitle, self.testItemList = parseSequence(sequenceFN)
    
    def getNumPages(self):
        return len(self.testItemList)
        
    def getPage(self, pageNum):
        pageName, argList, kargDict = getPageArgs(self.testItemList[pageNum])
        page = factories.loadPage(self.webSurvey, pageName, argList, kargDict)
        
        return page

    def getPageStr(self, pageNum):
        pageRow = self.testItemList[pageNum]
        
        chunkList = recChunkLine(pageRow)
        pageName = chunkList.pop(0)
        
        return pageName, chunkList


def parseSequence(sequenceFN, keepDirectives=False):
    with io.open(sequenceFN, "r", encoding='utf-8') as fd:
        testItemList = [row.rstrip("\n") for row in fd.readlines()]
    testItemList = [row for row in testItemList if row != '']
    
    if keepDirectives is False:
        testItemList = [row for row in testItemList if row[0] != '<']

    # Validate the test title
    sequenceTitle = testItemList.pop(0)
    if sequenceTitle[0] != "*":
        raise InvalidFirstLine(sequenceTitle)
    
    # Now that we've validated this is the sequence title,
    # get rid of the '*'
    sequenceTitle = sequenceTitle[1:]

    return sequenceTitle, testItemList


def _parse(txt, startDelim, endDelim, startI):
    '''
    For embedded structures, finds the appropriate start and end of one
    
    Given:
    [[0 0] [0 1] ] [2 3 4]
    This would return the indicies for:
    [[0 0] [0 1] ]
    > (0, 13)
    '''
    endI = None
    depth = 0
    startI = txt.index(startDelim, startI)
    for i in range(startI, len(txt)):
        if txt[i] == startDelim:
            depth += 1
        elif txt[i] == endDelim:
            depth -= 1
            if depth == 0:
                endI = i + 1
                break
    
    if endI is None:
        raise UnbalancedWrapperError(txt, startDelim, endDelim)
    
    return startI, endI


def _splitTxt(txt, splitItem):
    '''
    Split on whitespace or splitItem
    '''
    if splitItem is None:
        tmpDataList = txt.split()
    else:
        tmpDataList = txt.split(splitItem)
        tmpDataList = [row.strip() for row in tmpDataList if row.strip() != ""]
        
    return tmpDataList


def getPageArgs(pageRow):
    
    pageArgStr = recChunkLine(pageRow)
    pageName = pageArgStr.pop(0)
    
    # Get non-keyword arguments
    argList = []
    while len(pageArgStr) > 0:
        if '=' not in pageArgStr[0]:
            argList.append(pageArgStr.pop(0))
        else:
            break
    
    # Get keyword arguments
    kargDict = {}
    while len(pageArgStr) > 0:
        if len(pageArgStr) > 1 and isinstance(pageArgStr[1], type([])):
            key = pageArgStr.pop(0).split("=", 1)[0]
            value = pageArgStr.pop(0)
        else:
            key, value = pageArgStr.pop(0).split("=", 1)
        kargDict[key] = value
        
    return pageName, argList, kargDict


def recChunkLine(line, splitItem=None):
    '''
    Parses a line on space or splitItem.  Handles embedded lists.
    
    Given:
    a b c [d e f] [[g] h]
    Returns:
    ['a', 'b', 'c', ['d', 'e', 'f'], [['g'], 'h']]
    '''
    
    indicies = [0]
    indexList = []
    startIndex = 0
    endIndex = 0
    char1 = "["
    char2 = "]"
    while True:

        try:
            bracketStartIndex, endIndex = _parse(line, char1, char2,
                                                 startIndex)
        except ValueError:
            break
        
        indexList.append((startIndex, bracketStartIndex))
        indexList.append((bracketStartIndex, endIndex))
        
        indicies.append(endIndex)
        startIndex = endIndex
    
    if endIndex == 0:
        indexList.append((0, -1))
    else:
        indexList.append((endIndex, -1))
    
    # Make chunks
    chunkList = []
    i = 0
    while i < len(indexList) - 1:
        tmpData = line[indexList[i][0]:indexList[i][1]].strip()
        if char1 in tmpData:
            chunkList.append(recChunkLine(tmpData[1:-1], splitItem))
        elif tmpData != "":
            chunkList.extend((_splitTxt(tmpData, splitItem)))
        i += 1
    tmpData = line[indexList[-1][0]:].strip()
    if tmpData != "":
        splitData = _splitTxt(tmpData, splitItem)
        if splitData[0] == tmpData:
            splitData = _splitTxt(tmpData, None)
        chunkList.extend(splitData)
    
    return chunkList
