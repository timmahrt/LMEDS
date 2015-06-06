'''
Created on May 30, 2013

@author: timmahrt
'''


from lmeds import factories

# These are key words used in the forms to store the results of tests.
formOutputDict = {'prominence':'p',
                  'boundary': 'b',
                  'axb': 'axb',
                  'ab': 'ab', 
                  }


class TestSetupError(Exception):

    def __init__(self, unknownKeyList, *args, **kargs):
        super(TestSetupError, self).__init__(*args, **kargs)
        self.unknownKeyList = unknownKeyList

    def __str__(self):
        txtString = "ERROR: The following keys were found in 'sequence.txt' but they are not associated with any pages.  Please consult the test documentation or the administrator."
        
        unknownKeyStr = "\n".join(self.unknownKeyList)
        
        txtString += "\n" + unknownKeyStr
        
        return txtString


class EndOfTestSequenceException(Exception):
    
    
    def __init__(self, sequenceFN):
        self.sequenceFN = sequenceFN
    
    
    def __str__(self):
        return "End of test sequence: '%s'" % self.sequenceFN


class InvalidFirstLine(Exception):
    
    def __init__(self, item):
        self.item = item
        
    def __str__(self):
        return """ERROR: The first line in a sequence file must be 
        the sequence title (i.e. start with '*').\n\nFound '%s.""" % self.item
    
    
class InvalidSequenceFileError(Exception):
    
    def __init__(self, item):
        self.item = item
        
    def __str__(self):
        return """ERROR: The first command in a sequence file cannot be 
        a subsequence (i.e. start with '#').\n\nFound '%s'.""" % self.item
        


class TestSequence(object):
    
    
    def __init__(self, webSurvey, sequenceFN):
        self.sequenceFN = sequenceFN
    
        self.webSurvey = webSurvey
        self.sequenceTitle, self.testItemList = self.quickParse()

    
    def getNumPages(self):
        return len(self.testItemList)
    
    
    def getPage(self, pageNum):
        
        # Fetching page text from sequence file
        pageName, pageArgStr = self.getPageStr(pageNum)
        
        # Get non-keyword arguments
        argList = [arg for arg in pageArgStr if "=" not in arg] # Args
        
        # Get keyword arguments
        kargDict = {}
        nonArgList = [arg.split("=", 1) for arg in pageArgStr if '=' in arg]
        for key, value in nonArgList:
            kargDict[key] = value
        
        page = factories.loadPage(self.webSurvey, pageName, argList, kargDict)
        
        return page
    
    
    def getPageStr(self, pageNum):
        pageRow = self.testItemList[pageNum]
#         tmpList = pageRow.split(" ")
#         pageName = tmpList[0]
#         pageArgStr = tmpList[1:]
        

        # Find lists
        indicies = [0]
        indexList = []
        indexList2 = []
        startIndex = 0
        endIndex = 0
        char1 = "["
        char2 = "]"
        text = pageRow
        while True:
            try:
                bracketStartIndex = text.index(char1, startIndex)
            except ValueError:
                break
            endIndex = text.index(char2, bracketStartIndex)
            
            indexList.append( (startIndex, bracketStartIndex-1))
            indexList.append( (bracketStartIndex+1, endIndex))
            
            indicies.append(endIndex)
            startIndex = endIndex + 1
        
        if endIndex == 0:
            indexList.append( (0, -1))
        else:
            indexList.append( (endIndex + 1, -1) )
        
        # Make chunks
        chunkList = []
#         for i in xrange(len(indicies) - 1):
#             chunkList.append(text[i:i+1])
        i = 0
        while i < len(indexList) - 1:
            tmpData = text[indexList[i][0]:indexList[i][1]].strip()
            if tmpData != "":
                chunkList.extend((tmpData.split()))
#             print indexList[i], text[indexList[i][0]:indexList[i][1]]
            tmpData = text[indexList[i+1][0]:indexList[i+1][1]].strip()
            if tmpData != "":
#                 chunkList.append(tmpData.replace(" ", ","))
                chunkList.append(tmpData.split())
#             print indexList[i+1], text[indexList[i+1][0]:indexList[i+1][1]], "\n"
            i += 2
        tmpData = text[indexList[-1][0]:].strip()
        if tmpData != "":
            chunkList.extend(tmpData.split())
        
        pageName = chunkList.pop(0)
        
        return pageName, chunkList
        
#         pageArgStr.
#         
#         return pageName, pageArgStr
        
    
    def quickParse(self):
        data = open(self.sequenceFN, "rU").read()
        testItemList = data.split("\n")
        testItemList = [row.strip() for row in testItemList]
        testItemList = [row for row in testItemList if row != '']

        # Validate the test title
        sequenceTitle = testItemList.pop(0)
        if sequenceTitle[0] != "*":
            raise InvalidFirstLine(sequenceTitle)
        
        # Now that we've validated this is the sequence title, get rid of the '*'
        sequenceTitle = sequenceTitle[1:]

        return sequenceTitle, testItemList
    

    def parse_old(self):
        data = open(self.sequenceFN, "r").read()
        testItemList = data.split("\n")
        
        # Remove lines that users can use to separate sections
        testItemList = [line for line in testItemList if not self._isSeparatingString(line)]
        
        # Split items into argument lists
        keyValueList = [row.split(" ") for row in testItemList]
#         keyValueList = [(row[0], [item for item in row[1:] if item.strip() != ""]) for row in keyValueList
#                         if row[0].strip() != ""]
        
        tmpKeyValueList = []
        for row in keyValueList:
            if row[0].strip() != "":
                itemKey = row[0]
                tmpList = [arg for arg in row[1:] if arg != ''] # Filter out emptry strings (how are these appearing?)
                argList = [arg for arg in tmpList if "=" not in arg] # Args
                nonArgList = [arg.split("=", 1) for arg in row[1:] if '=' in arg]
                # Kargs
                kargDict = {}
                for key, value in nonArgList:
                    kargDict[key] = value
                tmpKeyValueList.append( (itemKey, argList, kargDict) )
        
        keyValueList = tmpKeyValueList
        
        # The first item is the sequence title, uniquely identifying this test
        sequenceTitle = keyValueList.pop(0)[0]
        if sequenceTitle[0] != "*":
            raise InvalidFirstLine(sequenceTitle)
        
        # Now that we've validated this is the sequence title, get rid of the '*'
        sequenceTitle = sequenceTitle[1:]
        
        # Extract the subsequencies of the test.  There is always at least implicit
        # subsequence ('main') and possibly other, user-defined ones.
        sequenceDict = {"main":[],}
        lastKey = "main"
        for i, keyValuePair in enumerate(keyValueList):
            key, valueList, valueDict = keyValuePair
            
            # At least the first item should be a runnable item and not a subsequence definition
            if i == 0 and key[0] == '#':
                raise InvalidSequenceFileError(key)
            
            # Handle new subsequence
            if key[0] == '#':
                lastKey = key[1:]
                
                assert(lastKey not in sequenceDict.keys())
                sequenceDict[lastKey] = []
            
            # Continue adding instructions to the current sequence   
            else:
                sequenceDict[lastKey].append((key, valueList, valueDict))
        
        # No subsequence should have zero length
        for valueList in sequenceDict.values():
            assert(len(valueList) > 0)
        
        return sequenceTitle, sequenceDict    
    
    
    def getNextPage(self, lastPage):
    
        # Exit now if there is no next page
        if lastPage == []:
            raise EndOfTestSequenceException(self.sequenceFN)
    
        sequenceTitle, routineDict = self.parse()
    
        # The details for the last page
        subroutine = lastPage[-1][0]
        prevPageNum = lastPage[-1][1]
        
        # Increment the page by one
        newPageNum = prevPageNum + 1
        
        # Pop the stack if we're done with this subroutine
        maxSubroutineLen = len(routineDict[subroutine])
        if newPageNum >= maxSubroutineLen:
            nextPage = self.getNextPage(lastPage[:-1])[1]
            
        # Otherwise, continue on with this subroutine
        else:
            task = routineDict[subroutine][newPageNum]
            nextPage = lastPage[:-1] + [(subroutine, newPageNum, task)]
            
            # Check for new subroutine, if so, add it to the stack
            if task[0][0] == '$':
                newSub = task[0][1:]
                newSubPage = 0
                newSubTask = routineDict[newSub][newSubPage]
                
                nextPage += [(newSub, newSubPage, newSubTask)]
            
        return sequenceTitle, nextPage
    
    
    #def isPageOfPageType(pageNumber, pageType):
    #    keyValueList = parseTestSequence()
    #    return keyValueList[pageNumber] == pageType
    #    
    #
    def getOutputKeys(self):
        '''
        This function retrieves all of the output keys used in the form for this sequence file
        '''
        keyValueList = self.iterate()
        testTypeList = [item[-1][2][0] for item in keyValueList]
        testTypeList = list(set(testTypeList))
        
        # Remove keys that don't store results
        testTypeList = [item for item in testTypeList if item in formOutputDict.keys()]
        
        usedOutputKeys = [formOutputDict[testType] for testType in testTypeList]
        
        return usedOutputKeys
    #
    #def parseTestSequence():
    #    data = open(constants.sequenceFile, "r").read()
    #    testItemList = data.split("\n")
    #    keyValueList = [row.split(" ") for row in testItemList]
    #    keyValueList = [(row[0], [item for item in row[1:] if item.strip() != ""]) for row in keyValueList
    #                    if row[0].strip() != ""]
    #    
    #    # Find any unknown keys
    #    unknownKeyList = []
    #    keyList = [row[0] for row in keyValueList]
    #    keyList = list(set(keyList))
    #    for key in keyList:
    #        if key not in pageTemplates.knownKeyList:
    #            unknownKeyList.append(key)
    #    
    #    # End the test if there are any keys in sequence.txt that we did not expect
    #    if len(unknownKeyList) > 0:
    #        raise TestSetupError(unknownKeyList)
    #        
    #    
    #    return keyValueList
    
    
    def _isSeparatingString(self, text):
        '''
        Returns false if there is at least one alphanumeric character
        '''
        isComment = True
        for char in text:
            isComment &= not char.isalnum()
            
        return isComment
    
    
    def iterate(self):
        subroutineList = []
        lastSubroutine = [('main', 0, ('login', [])),]
        
        try:
            while True:
                lastSubroutine = self.getNextPage(lastSubroutine)[1]
                subroutineList.append(lastSubroutine)
        except EndOfTestSequenceException:
            pass # End of test detected
            
        return subroutineList


if __name__ == "__main__":
    from lmeds import rptMain
    survey = rptMain.WebSurvey("demo", "sequence2.txt", "english.txt", False)
    ts = TestSequence(survey, "/Users/tmahrt/Sites/tests/demo/sequence2.txt")
    for pageNum in xrange(ts.getNumPages()):
        print ts.getPageStr(pageNum)
    
#     page = ts.getPage(3)
#     print page.getHTML()
    pass
        



