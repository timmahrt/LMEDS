'''
Created on Jul 15, 2014

@author: tmahrt
'''

import os
import sys
from os.path import dirname, abspath

os.chdir(dirname(dirname(abspath(__file__))))
sys.path.append(dirname(dirname(os.path.split(abspath(__file__))[0])))

from lmeds.io import sequence
from lmeds.io import loader

from lmeds.pages import abstract_pages


def checkSequenceFile(survey):
    
    seq = sequence.TestSequence(survey, survey.sequenceFN)

    for pageNum in xrange(seq.getNumPages()):
        try:
            page = seq.getPage(pageNum)
        except TypeError:
            print("Page %d: Problem with the number of arguments" % pageNum)
            continue
        except (abstract_pages.FileDoesNotExist,
                loader.TextNotInDictionaryException), e:
            print("Page %d: %s" % (pageNum, e))
            continue
        
        try:
            page = page.getHTML()
        except:
            errStr = "Page %d: Problem with at least one of the arguments: %s"
            print(errStr % (pageNum, seq.testItemList[pageNum]))
            continue

if __name__ == "__main__":
    pass
