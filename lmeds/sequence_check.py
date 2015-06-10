'''
Created on Jul 15, 2014

@author: tmahrt
'''

import sys
CODE_ROOT = ""
sys.path.append(CODE_ROOT)

from lmeds import sequence
from lmeds import loader

from lmeds.pages import abstractPages


def checkSequenceFile(survey):
    
    seq = sequence.TestSequence(survey, survey.sequenceFN)

    for pageNum in xrange(seq.getNumPages()):
        try:
            page = seq.getPage(pageNum)
        except TypeError:
            print "Page %d: Problem with the number of arguments" % pageNum
            raise
        except (abstractPages.FileDoesNotExist,
                loader.TextNotInDictionaryException), e:
            print "Page %d: %s" % (pageNum, e)
            continue
        
        try:
            page = page.getHTML()
        except:
            errStr = "Page %d: Problem with at least one of the arguments: %s"
            print errStr % (pageNum, seq.testItemList[pageNum])
            raise
