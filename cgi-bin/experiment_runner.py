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
from os.path import join
import datetime

try:
    from StringIO import StringIO  # Python 2
except ImportError:
    from io import StringIO  # Python 3
    
# The local server is started one level above cgi-bin.  The web server starts
# in cgi-bin. Try to move into cgi-bin.  If we can't, we're already there.
# If the code doesn't start in cgi-bin or one level above cgi-bin, probably
# nothing will work.  (You could try manually moving to cgi-bin by giving
# the full path).
try:
    os.chdir("cgi-bin")
except OSError:
    pass 

# This should point to the directory that includes the python package /lmeds
sys.path.append("..")
# Creates files that I don't have permissions to access
# cgitb.enable(display=0, logdir="../error_logs")
cgitb.enable()

from lmeds import lmeds_main
from lmeds.lmeds_io import sequence
from lmeds.utilities import constants
from lmeds.utilities import utils
from lmeds.user_scripts import generate_language_dictionary as gen_dict
from lmeds.user_scripts import sequence_check
from lmeds.user_scripts import get_test_duration
from lmeds.user_scripts import post_process_results


class Logger(object):
    '''
    By default logs in html to stdout, but can also log to a txt file
    '''
    def __init__(self, fn=None):
        self.fn = fn
        self.outputList = []
        
        if fn is None:
            lineSplitter = "<br />\n"
        else:
            lineSplitter = "\n"
        self.lineSplitter = lineSplitter
    
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    
    def __exit__(self, errType, errValue, errTraceback):
        self.outputList.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout
        
        outputTxt = self.lineSplitter.join(self.outputList) + self.lineSplitter
        if self.fn is None:
            print(outputTxt)
        else:
            with open(self.fn, "w") as fd:
                fd.write(outputTxt)
            
        if errValue != None:
            print("Error occurred in running script. "
                  "Please see logfile (/lmeds/tests/[project-name]/logs)")
        elif self.fn is not None:
            print("Script finished.  For more information please see logfile"
                  "(/lmeds/tests/[project-name]/logs)")
        
        return False

    
def runExperiment(leafFolder, sequenceFile, languageFile, disableRefresh,
                  audioExtList=None, videoExtList=None,
                  allowUtilityScripts=False, allowUsersToRelogin=False,
                  individualSequences=False):

    form = cgi.FieldStorage(keep_blank_values=True)

    # Utility scripts that override the main functionality
    keyList = ["get_test_duration", "sequence_check", "create_dictionary",
               "update_dictionary", "crop_dictionary", "post_process_results",
               ]
    keyDict = {}
    for key in keyList:
        if key in form:
            keyDict[key] = utils.decodeUnicode(form[key].value.lower())
    
    if allowUtilityScripts and len(keyDict) > 0:
        
        # Get experiment and sequence information
        surveyRoot = join(constants.rootDir, "tests", leafFolder)
        
        timestampFmt = '{:%Y-%m-%d_%H-%M-%S}'
        projectName = sequence.parseSequence(join(surveyRoot, sequenceFile))[0]
        outputDir = join(surveyRoot, "output", projectName)
        loggerPath = join(surveyRoot, "logs")
        utils.makeDir(loggerPath)
        
        print('Content-Type: text/html')
        print("\n\n")

        if "create_dictionary" in keyDict.keys():

            with Logger() as output:
                print("Creating dictionary...")
                gen_dict.generateLanguageDictionary("new",
                                                    leafFolder,
                                                    sequenceFile,
                                                    languageFile)
                

        if "update_dictionary" in keyDict.keys():
            with Logger() as output:
                print("Updating dictionary...")
                gen_dict.generateLanguageDictionary("update",
                                                    leafFolder,
                                                    sequenceFile,
                                                    languageFile)

        if "crop_dictionary" in keyDict.keys():
            with Logger() as output:
                print("Cropping dictionary...")
                gen_dict.generateLanguageDictionary("crop",
                                                    leafFolder,
                                                    sequenceFile,
                                                    languageFile)

        if "get_test_duration" in keyDict.keys():
            with Logger() as output:
                print("Getting experiment duration...")
            now = timestampFmt.format(datetime.datetime.now())
            fn = now + "get_duration.txt"
            with Logger(join(loggerPath, fn)) as output:
                get_test_duration.printTestDuration(outputDir)
            
        if "post_process_results" in keyDict.keys():
            with Logger() as output:
                print("Post processing results...")
            now = timestampFmt.format(datetime.datetime.now())
            fn = now + "_post_process_results.txt"
            with Logger(join(loggerPath, fn)) as output: 
                post_process_results.postProcessResults(leafFolder,
                                                        sequenceFile,
                                                        True)
            

    survey = lmeds_main.WebSurvey(leafFolder, sequenceFile, languageFile,
                                  disableRefresh, audioExtList=audioExtList,
                                  videoExtList=videoExtList,
                                  allowUsersToRelogin=allowUsersToRelogin,
                                  individualSequences=individualSequences)

    # For utility scripts that need the survey:
    if allowUtilityScripts and len(keyDict) > 0:

        if "sequence_check" in keyDict.keys():
            with Logger() as output:
                print("Checking sequence file for errors...")
                sequence_check.checkSequenceFile(survey)
            
        print("<br /><br />Done")
        exit()

    
    # The main survey
    survey.run(form)
    