# -*- coding: utf-8 -*-
'''
Created on Mar 28, 2013

@author: timmahrt
'''

from os.path import join

import constants

import codecs
#f = codecs.open('unicode.rst', encoding='utf-8')


    
class TextNotInDictionaryException(Exception):
    
    def __init__(self, txtKey):
        self.txtKey = txtKey
        self.dictionaryFN = textDict.sourceFN
        
    def __str__(self):
        errorTxt = "Text key <<%s>> not in dictionary file <<%s>\n\nPlease add text key to dictionary and try again."
        
        return errorTxt % (self.txtKey, self.dictionaryFN)
    

def loadTxt(fn):
    txt = codecs.open(fn, "r", encoding="utf-8").read()
    #txt = open(fn, "r").read()
    txtList = txt.split("\n")
    txtList = [txt.strip() for txt in txtList if txt != ""]

    return txtList


class TextDict(object):
    
    
    def __init__(self, fn):
        self.textFN = fn
        self.textDict = self._parse()
        
        
    def _parse(self):
            
        data = codecs.open(self.textFN, "r", encoding="utf-8").read()
        testItemList = data.split("\n")
        
        # Remove lines that users can use to separate sections
#         testItemList = [line for line in testItemList if not self._isSeparatingString(line)]
        
        # Split items into argument lists
#         keyValueList = testItemList
#         keyValueList = [row for row in testItemList]
#         keyValueList = [(row[0], [item for item in row[1:] if item.strip() != ""]) for row in keyValueList
#                         if row[0].strip() != ""]
        
        keyValueList = self._findSections(testItemList, "-")
        
        parsedTextDict = {}
        for key, subList in keyValueList.items():
            subKeyValueList = self._findSections(['',] + subList, "=")
            parsedTextDict.update(subKeyValueList)
             
        for key, textList in parsedTextDict.items():
            parsedTextDict[key] = "\n".join(textList).strip()
            
        return parsedTextDict
    
        
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
            if key != None:
                someDict[key] = valueList
                valueList = []
                
        def safeCheck(string, char):
            retValue = False
            if len(string) > 0:
                if string[0] == char:
                    retValue = True
            
            return retValue
        
        lastKey = None
        lastList = []
        
        i = 0
        sectionDictionary = {}
        while i + 2 < len(textList):
            
            # New section
            if safeCheck(textList[i], demarcator) and safeCheck(textList[i+2],demarcator):
                newSection(lastKey, lastList, sectionDictionary)
                lastKey = textList[i+1]
                lastList = []
                i += 3
            # Still on old section
            else:
                lastList.append(textList[i])
                i += 1
            
            newSection(lastKey, lastList, sectionDictionary)
            
        return sectionDictionary
        
    def getText(self, key):
        return self.textDict[key]


textDict = None # textDict singleton
def initTextDict(fn):
    global textDict
    textDict = TextDict(fn)


def getText(key):
    try:
        returnText = textDict.getText(key)
    except KeyError:
        raise TextNotInDictionaryException(key)
    
    return returnText


if __name__ == "__main__":
    
    text = TextDict("/Users/timmahrt/Sites/english.txt")
    print "hello"
    
    print text.getText("prominence post boundary instructions short")

    
    for key in text.textDict.keys():
        print key, len(text.textDict[key])
