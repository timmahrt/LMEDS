# -*- coding: utf-8 -*-
'''
Created on Mar 28, 2013

@author: timmahrt
'''


import io

NULL_SECTION = "000_entries_with_no_topic"


class BadlyFormattedTextError(Exception):
    '''
    A generic error that is used whenever a string in the text dictionary is
    improperly formatted.
    '''
    
    def __init__(self, errorTxt, txtKey, textDict):
        super(BadlyFormattedTextError, self).__init__()
        
        self.errorTxt = errorTxt
        self.txtKey = txtKey
        self.dictionaryFN = textDict.sourceFN
        
    def __str__(self):
        prefixStr = "For text key <<%s>> in dictionary file <<%s>>: "
        prefixStr %= (self.txtKey, self.dictionaryFN)
        
        return prefixStr + self.errorTxt


class SpaceInKeyError(Exception):
    
    def __init__(self, key):
        super(SpaceInKeyError, self).__init__()
        
        self.key = key
        
    def __str__(self):
        errorStr = ("Spaces not allowed in dictionary keys.  "
                    "Space found in key '%s'")
        
        return errorStr % self.key


class TextNotInDictionaryException(Exception):
    
    def __init__(self, txtKey, textDict):
        super(TextNotInDictionaryException, self).__init__()
        self.txtKey = txtKey
        self.dictionaryFN = textDict.sourceFN
        
    def __str__(self):
        errorTxt = ("Text key(s) [%s] not in dictionary file [%s]\n\n"
                    "Please add text key to dictionary and try again.")
        
        return errorTxt % (str(self.txtKey), self.dictionaryFN)
    

def loadTxtFile(fn):
    with io.open(fn, "r", encoding="utf-8") as fd:
        txt = fd.read()
    txtList = txt.splitlines()
    
    # Removes redundant whitespace
    txtList = [" ".join(txt.split()) for txt in txtList]
    
    # Remove empty rows
    txtList = [row for row in txtList if row != ""]

    return txtList


def loadTxtFileWHTML(fn):
    with io.open(fn, "r", encoding="utf-8") as fd:
        txtList = [row.rstrip("\n") for row in fd.readlines()]
    
    newTxtList = []
    for row in txtList:
        if row == "":
            continue
        if row[0] == "<":
            newTxtList.append(row)
        else:
            newTxtList.extend(" ".join(row.split()))
    txtList = newTxtList
    
    txtList = [row for row in txtList if row != ""]  # Remove empty rows

    return txtList


def splitTranscript(fnFullPath):
    wordList = loadTxtFile(fnFullPath)
    returnList = []
    for line in wordList:
        if '<' in line:  # HTML check
            continue
        returnList.append(line.split(" "))
    
    return returnList


def getNumWords(fnFullPath):
    '''
    Get number of words in a transcript
    '''
    transcriptList = splitTranscript(fnFullPath)
    numOutputs = sum([len(row) for row in transcriptList])

    return numOutputs


class TextString(object):

    def __init__(self, wordString):
        self.wordString = wordString

    def __repr__(self):
        return self.wordString


class TextDict(object):
    
    def __init__(self, fn):
        self.sourceFN = fn
        self.textDict, self.sectionsDict = self._parse()
    
    def _parse(self):
        
        with io.open(self.sourceFN, 'r', encoding="utf-8") as fd:
            data = fd.read()
        
        # Special case -- no section before the first text entries
        # insert a dummy section
        i = data.index('---')
        try:
            j = data.index('===')
        except ValueError:
            pass
        else:
            if j < i:
                demarc = "-" * 20
                sectionName = NULL_SECTION
                newSection = "\n%s\n%s\n%s\n\n" % (demarc, sectionName, demarc)
                data = newSection + data
        
        testItemList = data.splitlines()
        
        keyValueList = self._findSections(testItemList, "-")
        
        parsedTextDict = {}
        sectionsDict = {}
        for key, subList in keyValueList.items():
            subKeyValueDict = self._findSections(['', ] + subList, "=")
            parsedTextDict.update(subKeyValueDict)
            
            sectionsDict[key] = subKeyValueDict.keys()
             
        for key, textList in parsedTextDict.items():
            parsedTextDict[key] = " ".join(textList).strip()
            
        return parsedTextDict, sectionsDict
    
    def _isSeparatingString(self, text):
        '''
        Returns false if there is at least one alphanumeric character
        '''
        isComment = True
        for char in text:
            isComment &= not char.isalnum()
            
        return isComment
    
    def _findSections(self, textList, demarcator):
        
        def newSection(key, valueList, someDict):
            if key is not None:
                someDict[key] = valueList
                valueList = []
                
        def safeCheck(stringList, i, char):
                
            retValue = False
            if i < len(stringList):
                string = stringList[i]
                if len(string) > 0:
                    if string[0] == char:
                        retValue = True
            
            return retValue
        
        lastKey = None
        lastList = []
        
        i = 0
        sectionDictionary = {}
        while i < len(textList):
            
            # New section
            firstCheck = safeCheck(textList, i, demarcator)
            if firstCheck and safeCheck(textList, i + 2, demarcator):
                newSection(lastKey, lastList, sectionDictionary)
                lastKey = textList[i + 1]
                lastList = []
                i += 3
            # Still on old section
            else:
                lastList.append(textList[i])
                i += 1
        
        newSection(lastKey, lastList, sectionDictionary)
            
        return sectionDictionary
        
    def getText(self, key):
        if " " in key:
            raise SpaceInKeyError(key)
        
        try:
            returnText = self.textDict[key]
        except KeyError:
            raise TextNotInDictionaryException(key, self)
        
        return returnText

    def batchGetText(self, keyList):
        errorList = []
        retDict = {}
        for key in keyList:
            try:
                retDict[key] = self.getText(key)
            except TextNotInDictionaryException:
                errorList.append(key)
    
        if len(errorList) > 0:
            raise TextNotInDictionaryException(errorList, self)
        
        return retDict


class EmptyDict(object):
    
    def getText(self, key):
        return None
    
    def batchGetText(self, keyList):
        retDict = {}
        for key in keyList:
            retDict[key] = self.getText(key)
        
        return retDict
