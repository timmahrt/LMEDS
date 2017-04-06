'''
Created on Nov 17, 2013

@author: timmahrt
'''

import sys
import os
import numbers

# Python 2-to-3 compatibility hack
try:
    from itertools import izip_longest as zip_longest  # Python 2.x
except ImportError:
    from itertools import zip_longest  # Python 3.x

import functools
import math


class UnbalancedListsError(Exception):
    
    def __init__(self, listOfLists):
        super(UnbalancedListsError, self).__init__()
        
        self.listOfLists = listOfLists
        
    def __str__(self):
        retStr = "All sublists must be the same length.\n"
        for subList in self.listOfLists:
            retStr += "Length:%04d,List:%s\n" % (len(subList), subList)
        
        return retStr


def decodeUnicode(inputStr):
    
    # Python 2-to-3 compatibility hack
    try:
        outputStr = inputStr.decode("utf-8")  # Python 2.x str, to unicode
    except AttributeError:
        outputStr = inputStr  # Python 3.x, already unicode
        
    return outputStr


def outputUnicode(outputStr):
    # Python 2-to-3 compatibility hack
    try:
        sys.stdout.buffer.write(outputStr.encode('utf-8'))  # Python 3.x
    except AttributeError:
        print(outputStr.encode('utf-8'))  # Python 2.x
        

def detectLineEnding(txt):
    returnText = None  # A file may have no newlines
    endingsList = ["\r\n", "\n", "\r"]
    truthList = []
    
    for lineEnding in endingsList:
        truthList.append(lineEnding in txt)
        if lineEnding in txt:
            returnText = lineEnding
            break
            
    # Obviously, this will not be true if the line ending is "\r\n"
    # -- I'm not sure what I intended with this piece of code
#     assert(sum(truthList) <= 1)
    
    return returnText


def _getMatchFunc(pattern):
    '''
    An unsophisticated pattern matching function
    '''
    
    # '#' Marks word boundaries, so if there is more than one we need to do
    #    something special to make sure we're not mis-representings them
    assert(pattern.count('#') < 2)

    def startsWith(subStr, fullStr):
        return fullStr[:len(subStr)] == subStr
            
    def endsWith(subStr, fullStr):
        return fullStr[-1 * len(subStr):] == subStr
    
    def inStr(subStr, fullStr):
        return subStr in fullStr

    # Selection of the correct function
    if pattern[0] == '#':
        pattern = pattern[1:]
        cmpFunc = startsWith
        
    elif pattern[-1] == '#':
        pattern = pattern[:-1]
        cmpFunc = endsWith
        
    else:
        cmpFunc = inStr
    
    return functools.partial(cmpFunc, pattern)


def findFiles(path, filterPaths=False, filterExt=None, filterPattern=None,
              skipIfNameInList=None, stripExt=False):
    
    fnList = os.listdir(path)
       
    if filterPaths is True:
        fnList = [folderName for folderName in fnList
                  if os.path.isdir(os.path.join(path, folderName))]

    if filterExt is not None:
        splitFNList = [[fn, ] + list(os.path.splitext(fn)) for fn in fnList]
        fnList = [fn for fn, name, ext in splitFNList if ext == filterExt]
        
    if filterPattern is not None:
        splitFNList = [[fn, ] + list(os.path.splitext(fn)) for fn in fnList]
        matchFunc = _getMatchFunc(filterPattern)
        fnList = [fn for fn, name, ext in splitFNList if matchFunc(name)]
    
    if skipIfNameInList is not None:
        targetNameList = [os.path.splitext(fn)[0] for fn in skipIfNameInList]
        fnList = [fn for fn in fnList
                  if os.path.splitext(fn)[0] not in targetNameList]
    
    if stripExt is True:
        fnList = [os.path.splitext(fn)[0] for fn in fnList]
    
    fnList.sort()
    return fnList


def makeDir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def safeZip(listOfLists, enforceLength):
    
    if enforceLength is True:
        length = len(listOfLists[0])
        if not all([length == len(subList) for subList in listOfLists]):
            raise UnbalancedListsError(listOfLists)
    
    return zip_longest(*listOfLists)


def recNestedListToStr(targetList):
    
    strList = []
    for item in targetList:
        if isinstance(item, list):
            item = recNestedListToStr(item)
        if isinstance(item, numbers.Real):
            item = str(item)
        strList.append(item)
        
    retStr = "[%s]" % ",".join(strList)
    return retStr


def orderOfMagnitude(val):
    return int(math.floor(math.log10(val)))
    

class FilesDoNotExist(BaseException):
    
    def __init__(self, path, nameList, allFlag):
        super(FilesDoNotExist, self).__init__()
        self.path = path
        self.nameList = nameList
        self.allFlag = allFlag
        
    def __str__(self):
        fnTxt = ", ".join(name for name in self.nameList[:-1])
        fnTxt += ", or %s" % self.nameList[-1]
        
        retString = ("At least one of the following files %s does not "
                     "exist in folder %s. ")
        
        if self.allFlag is True:
            retString += "All of them must exist."
        else:
            retString += "At least one of them must exist."
        
        return retString % (fnTxt, self.path)

