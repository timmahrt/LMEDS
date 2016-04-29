'''
Created on Apr 29, 2016

@author: Tim
'''

import os
from os.path import join
import sys

cwd = os.path.dirname(os.path.realpath(__file__))
_root = os.path.split(cwd)[0]
sys.path.append(_root)

from lmeds import rpt_main

leafFolder = "lmeds_demo"
sequenceFile = "sequence.txt"
languageFile = "english.txt"
disableRefresh = False
audioExtList = [".ogg", ".mp3"]

survey = rpt_main.WebSurvey(leafFolder, sequenceFile, languageFile,
                            disableRefresh, audioExtList=audioExtList)

for i in range(survey.testSequence.getNumPages()):
    page = survey.testSequence.getPage(i)
    survey.buildPage(i, "", page, "no_name", survey.testSequence,
                     survey.sourceCGIFN)
