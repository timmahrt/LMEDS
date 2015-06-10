'''
Created on Mar 2, 2014

@author: tmahrt

The only function of this code is to add LMEDS to the current path and
execute the desired code.

-----
instructions
-----

COPY THIS FILE TO THE .cgi FOLDER
'''

import cgi
import cgitb
cgitb.enable()

import sys

# This should point to the directory /lmeds/
sys.path.append("/Users/tmahrt/Dropbox/workspace/LMEDS/lmeds")


from lmeds import rpt_main


def runExperiment(leafFolder, sequenceFile, languageFile, disableRefresh):
    survey = rpt_main.WebSurvey(leafFolder, sequenceFile,
                                languageFile, disableRefresh)
    survey.run()
