#!/usr/bin/env python
'''
Created on Jul 22, 2015

@author: tmahrt
'''

import os
from os.path import join
import sys
import argparse
import shutil

from os import path
from os.path import dirname, abspath


os.chdir(dirname(dirname(abspath(__file__))))
sys.path.append("..")

from lmeds.io import sequence
from lmeds import rpt_main
from lmeds.io import loader
from lmeds.utilities import user_script_helper

sectionHeaderLength = 30
keywordLength = 20
sectionTemplate = "%s\n%%s\n%s\n\n" % ("-" * sectionHeaderLength,
                                       "-" * sectionHeaderLength)
keywordTemplate = "%s\n%%s\n%s\n\n%%s\n\n" % ("=" * keywordLength,
                                              "=" * keywordLength)


def _removeDuplicates(tmpList):
    returnList = []
    for value in tmpList:
        if value not in returnList:
            returnList.append(value)
    
    return returnList


def generateLanguageDictionary(mode, testName, sequenceFN, outputFN):
    
    mode = mode.lower()
    assert(mode in ['update', 'crop', 'new'])
    
    webSurvey = rpt_main.WebSurvey(testName, sequenceFN, None,
                                   disableRefreshFlag=True, sourceCGIFN=None)
    
    outputFNFullPath = join(webSurvey.surveyRoot, outputFN)
    
    keepTextStrings = mode in ['update', 'crop', ]
    oldDictionary = None
    if keepTextStrings:
        oldDictionary = loader.TextDict(outputFNFullPath)
    
    doCrop = mode in ['crop', ]
    
    ts = webSurvey.testSequence
    
    txtKeyDict = {}
    pageNameList = ["lmeds_interface", ]
    
    # Load all of the txtKeys
    
    # Special case, the main lmeds interface, which is not
    # a proper 'page' object
    for txtKey in webSurvey.textDict.keys():
        txtKeyDict.setdefault(txtKey, [])
        txtKeyDict[txtKey].append("lmeds_interface")
    
    # Load the regular cases
    for i in xrange(ts.getNumPages()):
        page = ts.getPage(i)
        if page.pageName not in pageNameList:
            pageNameList.append(page.pageName)
        
        for txtKey in page.textDict.keys():
            txtKeyDict.setdefault(txtKey, [])
            txtKeyDict[txtKey].append(page.pageName)

    # Preserve keys in the dictionary but not in the sequence file
    # A bit tricky, because pageNames in the dictionary are already classified
    # as alone or grouped with other pages.  We'll split them out here if
    # necessary and let the code recombine them later with the other paired
    # pages.
    if not doCrop and oldDictionary is not None:
        for pageName, txtKeyList in oldDictionary.sectionsDict.items():
            if "," in pageName:
                pageNameSubList = pageName.split(",")
            else:
                pageNameSubList = [pageName, ]
            for tmpPageName in pageNameSubList:
                if tmpPageName not in pageNameList:
                    pageNameList.append(tmpPageName)

                for txtKey in txtKeyList:
                    txtKeyDict.setdefault(txtKey, [])
                    txtKeyDict[txtKey].append(tmpPageName)

    
    # Invert the txtKeyDict so we can reference keys by pages
    invKeyDict = {}
    for txtString in txtKeyDict.keys():
        pageTuple = tuple(_removeDuplicates(txtKeyDict[txtString]))
        txtKeyDict[txtString] = pageTuple
        invKeyDict.setdefault(pageTuple, [])
        invKeyDict[pageTuple].append(txtString)
    
    # Create the section order (single page sections, followed by multipage)
    singlePages = [(pageName,) for pageName in pageNameList]
    comboPages = [pageTuple for pageTuple in invKeyDict.keys()
                  if len(pageTuple) > 1]
    outputPageNameList = singlePages + comboPages
    
    # Build output
    outputTxt = "\n\n"
    for pageTuple in outputPageNameList:
        keyStringList = invKeyDict[pageTuple]
        keyStringList.sort()
        
        outputTxt += sectionTemplate % ",".join(pageTuple)
        for keyString in keyStringList:
            
            textString = ""
            if keepTextStrings and keyString in oldDictionary.textDict.keys():
                textString = oldDictionary.textDict[keyString]
            
            outputTxt += keywordTemplate % (keyString, textString)
    
    # Exit without doing anything if the old dictionary exists and
    # we're in 'new' mode
    if mode == "new":
        try:
            assert(not os.path.exists(outputFNFullPath))
        except AssertionError:
            errorStr = ("Dictionary file '%s' already exists.  Please delete "
                        "it or input a different dictionary file")
            print(errorStr % outputFNFullPath)
            exit()
    
    # Create a backup
    if os.path.exists(outputFNFullPath):
        backupFN = (os.path.splitext(outputFNFullPath)[0] +
                    "_autobackup.txt")
        shutil.copy(outputFNFullPath, backupFN)

    open(outputFNFullPath, "w").write(outputTxt)
    

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', action='store', default="new", dest='mode',
                        choices=("update", "crop", "new"),
                        help=("'update' will add any new textkeys used in the "
                              "sequence file to the dictionary along with "
                              "their string values. "
                              "'crop' (same as update plus) will remove from "
                              "the dictionary any textkeys not used in the "
                              "sequence file."
                              "'new' (the default option) creates a new "
                              "dictionary from scratch. If a dictionary "
                              "already exists, then it does nothing."
                              ))
    parser.add_argument('test_name', action='store',
                        help=("The name of the root folder that stores the "
                              "test files"))
    parser.add_argument('sequence_fn', action='store',
                        help=("The sequence .txt file to extract textkeys "
                              "from"))
    parser.add_argument('output_fn', action='store',
                        help=("The dictionary .txt to output textkeys and "
                              "their value strings"))
    
    try:
        cmdArgs = user_script_helper.runScriptLogic(parser)
    except user_script_helper.InteractiveModeException:
        _mode = raw_input("Enter a mode (update, crop, or new):\n")
        _test_name = raw_input(("Enter the name of your test "
                                "(the root folder):\n"))
        _sequence_fn = raw_input("Enter the name of your sequence file:\n")
        _output_fn = raw_input(("Enter the name of the dictionary file to "
                                "write to:\n"))
    else:
        _mode = cmdArgs.mode
        _test_name = cmdArgs.test_name
        _sequence_fn = cmdArgs.sequence_fn
        _output_fn = cmdArgs.output_fn
    
    generateLanguageDictionary(_mode, _test_name,
                               _sequence_fn, _output_fn)
