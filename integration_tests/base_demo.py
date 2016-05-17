'''
Created on May 16, 2016

@author: tmahrt
'''

import os
from os.path import join
import sys

cwd = os.path.dirname(os.path.realpath(__file__))
_root = os.path.split(cwd)[0]
sys.path.append(_root)

from lmeds import lmeds_main

leafFolder = "lmeds_demo"
sequenceFile = "sequence.txt"
languageFile = "english.txt"
disableRefresh = False
audioExtList = [".ogg", ".mp3"]

survey = lmeds_main.WebSurvey(leafFolder, sequenceFile, languageFile,
                              disableRefresh, audioExtList=audioExtList)
