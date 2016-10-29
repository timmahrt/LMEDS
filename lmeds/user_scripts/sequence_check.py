#!/usr/bin/env python
'''
Created on Jul 15, 2014

@author: tmahrt
'''

import os
import sys
import argparse
from os.path import dirname, abspath, join

os.chdir(dirname(dirname(abspath(__file__))))
sys.path.append("..")

from lmeds import lmeds_main

from lmeds.lmeds_io import sequence
from lmeds.lmeds_io import loader

from lmeds.pages import abstract_pages
from lmeds.utilities import user_script_helper
from lmeds.utilities import utils


def checkSequenceFile(survey):
    
    outputDir = join(survey.outputDir, survey.testSequence.sequenceTitle)
    
    if not os.path.exists(outputDir):
        print("FYI: Output folder does not exist: '%s'" % outputDir)
    
    try:
        if len(utils.findFiles(outputDir, filterExt=".csv")) > 0:
            print("FYI: User data already exists in output folder")
    except OSError:
        pass
    
    seq = sequence.TestSequence(survey, survey.sequenceFN)
    numErrors = 0
    for pageNum in range(seq.getNumPages()):
    
        try:
            page = seq.getPage(pageNum)
        except TypeError:
            print("Page %d: Problem with the number of arguments" % pageNum)
            continue
        except (utils.FilesDoNotExist,
                loader.TextNotInDictionaryException) as e:
            print("Page %d: %s\n" % (pageNum, str(e)))
            numErrors += 1
            continue
        
        try:
            page = page.getHTML()
        except BaseException as e:
            errStr = ("Page %d: Problem with at least one of the arguments: "
                      "'%s'\n%s:%s\n")
            print(errStr % (pageNum, str(seq.testItemList[pageNum]), e.__class__.__name__, str(e)))
            numErrors += 1
            continue
    
    if numErrors == 0:
        print("No errors found in sequence file.")

if __name__ == "__main__":
    
    description = "Verifies that the sequence file is well formed"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('test_name', action='store',
                        help=("The name of the root folder that stores the "
                              "test files"))
    parser.add_argument('sequence_fn', action='store',
                        help=("The sequence .txt file"))
    parser.add_argument('language_fn', action='store',
                        help=("The language dictionary .txt file"))
    parser.add_argument('disable_refresh_flag', action='store',
                        help=("Disable the refresh button?  true or false?"))
    audioMsg = ('The audio file types used.  Separate with ","and no spaces.'
                'eg:.mp3,.ogg,.wav.  Default=.mp3,.ogg')
    parser.add_argument('audio_ext_list', action='store',
                        help=audioMsg)
    
    try:
        cmdArgs = user_script_helper.runScriptLogic(parser)
    except user_script_helper.InteractiveModeException:
        _test_name = raw_input(("Enter the name of your test "
                                "(the root folder):\n"))
        _sequence_fn = raw_input("Enter the name of your sequence file:\n")
        _language_fn = raw_input(("Enter the name of the language "
                                  "dictionary:\n"))
        _disable_refresh_flag = raw_input(("Disable the refresh button?  "
                                           "true or false?\n"))
        audioPrompt = ("Audio files to use (use commas, no spaces "
                       "eg:.mp3,.wav)\n")
        _audio_ext_list = raw_input(audioPrompt).split(",")
    else:
        _test_name = cmdArgs.test_name
        _sequence_fn = cmdArgs.sequence_fn
        _language_fn = cmdArgs.language_fn
        _disable_refresh_flag = cmdArgs.disable_refresh_flag
        
        if cmdArgs.audio_ext_list:
            _audio_ext_list = cmdArgs.audio_ext_list.split(",")
        else:
            _audio_ext_list = None
        
    if _disable_refresh_flag.lower() == 'true':
        _disable_refresh_flag = True
    elif _disable_refresh_flag.lower() == 'false':
        _disable_refresh_flag = False
    
    survey = lmeds_main.WebSurvey(_test_name, _sequence_fn, _language_fn,
                                  _disable_refresh_flag,
                                  audioExtList=_audio_ext_list)
    checkSequenceFile(survey)
