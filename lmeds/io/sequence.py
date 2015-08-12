'''
Created on May 30, 2013

@author: timmahrt
'''


from lmeds.pages import factories

# These are key words used in the forms to store the results of tests.
formOutputDict = {'prominence': 'p',
                  'boundary': 'b',
                  'axb': 'axb',
                  'ab': 'ab',
                  }


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
        return ("ERROR: The first line in a sequence file must be"
                "the sequence title (i.e. start with '*').\n\nFound '%s."
                ) % self.item
    
    
class InvalidSequenceFileError(Exception):
    
    def __init__(self, item):
        super(InvalidSequenceFileError, self).__init__()
        self.item = item
        
    def __str__(self):
        return ("ERROR: The first command in a sequence file cannot be"
                "a subsequence (i.e. start with '#').\n\nFound '%s'."
                ) % self.item


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
        argList = [arg for arg in pageArgStr if "=" not in arg]  # Args
        
        # Get keyword arguments
        kargDict = {}
        nonArgList = [arg.split("=", 1) for arg in pageArgStr if '=' in arg]
        for key, value in nonArgList:
            kargDict[key] = value
        
        page = factories.loadPage(self.webSurvey, pageName, argList, kargDict)
        
        return page
    
    def getPageStr(self, pageNum):
        pageRow = self.testItemList[pageNum]
        
        # Find lists
        indicies = [0]
        indexList = []
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
            
            indexList.append((startIndex, bracketStartIndex - 1))
            indexList.append((bracketStartIndex + 1, endIndex))
            
            indicies.append(endIndex)
            startIndex = endIndex + 1
        
        if endIndex == 0:
            indexList.append((0, -1))
        else:
            indexList.append((endIndex + 1, -1))
        
        # Make chunks
        chunkList = []
        i = 0
        while i < len(indexList) - 1:
            tmpData = text[indexList[i][0]:indexList[i][1]].strip()
            if tmpData != "":
                chunkList.extend((tmpData.split()))
            tmpData = text[indexList[i + 1][0]:indexList[i + 1][1]].strip()
            if tmpData != "":
                chunkList.append(tmpData.split())
            i += 2
        tmpData = text[indexList[-1][0]:].strip()
        if tmpData != "":
            chunkList.extend(tmpData.split())
        
        pageName = chunkList.pop(0)
        
        return pageName, chunkList
    
    def quickParse(self):
        data = open(self.sequenceFN, "rU").read()
        testItemList = data.split("\n")
        testItemList = [row.strip() for row in testItemList]
        testItemList = [row for row in testItemList if row != '']

        # Validate the test title
        sequenceTitle = testItemList.pop(0)
        if sequenceTitle[0] != "*":
            raise InvalidFirstLine(sequenceTitle)
        
        # Now that we've validated this is the sequence title,
        # get rid of the '*'
        sequenceTitle = sequenceTitle[1:]

        return sequenceTitle, testItemList
