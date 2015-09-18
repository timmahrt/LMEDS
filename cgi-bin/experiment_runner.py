'''
Created on Mar 2, 2014

@author: tmahrt

The only function of this code is to add LMEDS to the current path and 
execute the desired code.

This must stay in the same folder as the .cgi files
'''

import cgi
import cgitb

import sys
import os

# The local server is started one level above cgi-bin.  The web server starts in cgi-bin.
# Try to move into cgi-bin.  If we can't, we're already there.  If the code doesn't start
# in cgi-bin or one level above cgi-bin, probably nothing will work.  (You could
# try manually moving to cgi-bin by giving the full path).
try:
    os.chdir("cgi-bin")
except OSError:
    pass 

# This should point to the directory that includes the python package /lmeds
sys.path.append("..")
# cgitb.enable(display=0, logdir="../error_logs")  # Creates files that I don't have permissions to access
cgitb.enable()

from lmeds import rpt_main


def runExperiment(leafFolder, sequenceFile, languageFile, disableRefresh):
    survey = rpt_main.WebSurvey(leafFolder, sequenceFile, languageFile, disableRefresh)
    survey.run()
    