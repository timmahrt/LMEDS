#!/usr/bin/env python
'''
Created on Aug 9, 2015

@author: timmahrt
'''

import os
from os.path import join
import sys
import argparse
import io
import shutil

from os.path import dirname, abspath

os.chdir(dirname(dirname(abspath(__file__))))
sys.path.append("..")

from lmeds.lmeds_io import sequence
from lmeds.lmeds_io import user_response
from lmeds.lmeds_io import survey
from lmeds.lmeds_io import loader
from lmeds.utilities import utils
from lmeds.utilities import user_script_helper
from lmeds.utilities import constants
from lmeds.post_process import transpose_rpt
from lmeds.post_process import transpose_survey
from lmeds.post_process import transpose_choice

ASPECT_MEANING = "meaning"
ASPECT_ACOUSTICS = "acoustics"
ASPECT_WRITING = "writing"
ASPECT_IMAGINE = "imagine"


class EmptyUserDataFile(Exception):
    
    def __init__(self, fn):
        super(EmptyUserDataFile, self).__init__()
        self.fn = fn
        
    def __str__(self):
        errMsg = ("User results file '%s' contains no user data. "
                  "Remove file and try again.")
        return errMsg % self.fn


def extractFromTest(path, keyList, removeItemList=None, onlyKeepList=None):
    '''
    Extracts all matching keys from a user's results in an LMEDS test
    '''
    
    # Load all user data
    # -- separate the command name on each line from the rest of the line
    testSequenceDataList = []
    for fn in utils.findFiles(path, filterExt=".csv"):
        with io.open(join(path, fn), "r", encoding="utf-8") as fd:
            subjectDataList = [row.rstrip("\n") for row in fd.readlines()]
        subjectDataList = [line.split(",", 1) for line in subjectDataList]
        testSequenceDataList.append((fn, subjectDataList))
     
    for key in keyList:
        
        outputDir = join(path, key)
        utils.makeDir(outputDir)
         
        for fn, subjectDataList in testSequenceDataList:
            subjectDataSubsetList = []
            for line in subjectDataList:
                command = line[0]
                if command == key:
                    partialLine = line[1].split(';,')[0]
                    
                    skipOut = False
                    if removeItemList is not None:
                        for item in removeItemList:
                            if item in partialLine:
                                skipOut = True
                    if onlyKeepList is not None:
                        for item in onlyKeepList:
                            if item not in partialLine:
                                skipOut = True
                    if skipOut is True:
                        continue
                    subjectDataSubsetList.append(",".join(line))
            # Don't output a blank file
            if subjectDataSubsetList == []:
                continue
            
            with io.open(join(outputDir, fn), "w", encoding="utf-8") as fd:
                fd.write("\n".join(subjectDataSubsetList))


def removeDuplicates(path, overwrite=False):

    outputPath = join(path, "duplicates_removed")
    if overwrite is False:
        os.mkdir(outputPath)
    else:
        utils.makeDir(outputPath)
    
    anyDuplicatesFound = False
    
    for fn in utils.findFiles(path, filterExt=".csv"):
        
        with io.open(join(path, fn), "r", encoding="utf-8") as fd:
            data = fd.read()
        dataList = data.splitlines()
        
        try:
            outputList = [dataList[0], ]
        except IndexError:
            raise EmptyUserDataFile(fn)
        
        prevString = dataList[0].split(";,")[0].rsplit("]", 1)[0]
        for i in range(1, len(dataList)):
            curString = dataList[i].split(";,")[0].rsplit("]", 1)[0]
            
            if curString == prevString:
                if anyDuplicatesFound is False:
                    print("Duplicates removed:")
                    anyDuplicatesFound = True
                print("%s, %d, %s" % (fn, i, curString))
            else:
                outputList.append(dataList[i])
            
            prevString = curString
        
        # Special case: pop the last item in the sequence if it is 'login'
        # -- this happens when a user tries to log in to an experiment after
        #    already completing it
        if outputList[-1][:6] == "login," and len(outputList) > 1:
            outputList.pop(-1)
        
        with io.open(join(outputPath, fn), "w", encoding="utf-8") as fd:
            fd.write("\n".join(outputList))

    if anyDuplicatesFound is True:
        print("End of duplicates listing")
    

def agglutinateSpreadsheets(csvFNList, outputFN):
    
    csvDataList = []
    for fn in csvFNList:
        with io.open(fn, "r", encoding="utf-8") as fd:
            csvDataList.append(fd.readlines())
    
    outputDataList = []
    for rowList in utils.safeZip(csvDataList, enforceLength=True):
        rowList = [row.replace("\n", "") for row in rowList]
        outputDataList.append(",".join(rowList))
        
    outputTxt = "\n".join(outputDataList) + "\n"
    with io.open(outputFN, "w", encoding="utf-8") as fd:
        fd.write(outputTxt)


def postProcessResults(testName, sequenceFN, removeDuplicatesFlag,
                       removeItemList=None):
    
    rootPath = join(constants.rootDir, "tests", testName)
    txtPath = join(rootPath, "txt")
    tmpSequence = sequence.TestSequence(None, join(rootPath, sequenceFN))
    fullPath = join(rootPath, "output", tmpSequence.sequenceTitle)
    pathToData = fullPath
    
    if removeDuplicatesFlag is True:
        removeDuplicates(pathToData, True)
        pathToData = join(pathToData, "duplicates_removed")
    else:
        newPathToData = join(pathToData, "duplicates_not_removed")
        utils.makeDir(newPathToData)
        for fn in utils.findFiles(pathToData, filterExt=".csv"):
            shutil.copy(join(pathToData, fn), join(newPathToData, fn))
        pathToData = newPathToData
    
    outputPath = pathToData + "_results"
    
    userResponseList = []
    fnList = utils.findFiles(pathToData, filterExt=".csv")
    for fn in fnList:
        fullPath = join(pathToData, fn)
        userResponseList.append(user_response.loadUserResponse(fullPath))
    
    # Don't continue if files are of different lengths
    testLen = len(userResponseList[0])
    if not all([len(response) == testLen for response in userResponseList]):
        print("ERROR: Not all responses in folder %s are the same length"
              % pathToData)
        countDict = {}
        for fn, response in utils.safeZip([fnList, userResponseList], True):
            countDict.setdefault(len(response), [])
            countDict[len(response)].append(fn)
            
        keyList = list(countDict.keys())
        keyList.sort()
        for numLines in keyList:
            print("%d lines - %s" % (numLines, str(countDict[numLines])))
        exit(0)
    
    # Don't continue if pages are different
    pageNameList = [[(pageTuple[0], pageTuple[1]) for pageTuple in response]
                    for response in userResponseList]
    sameList = []
    fnListOfLists = []
    for fn, pageList in utils.safeZip([fnList, pageNameList], True):
        i = 0
        while True:
            if len(sameList) == i:
                sameList.append(pageList)
                fnListOfLists.append([])
            else:
                if sameList[i] == pageList:
                    fnListOfLists[i].append(fn)
                    break
                else:
                    i += 1
    
    if len(sameList) == 0:
        print("ERROR: There don't appear to be any test data in folder %s"
              % pathToData)
        exit(0)
        
    if len(sameList) != 1:
        print("ERROR: User data doesn't agree.  Filenames printed on "
              "different lines differ in their pages.")
        
        for subFNList in fnListOfLists:
            print(", ".join(subFNList))
            
    # Extract the different tests users completed
    uniquePageList = []
    for pageTuple in pageNameList[0]:
        pageName = pageTuple[0]
        if pageName not in uniquePageList:
            uniquePageList.append(pageName)
    
    extractFromTest(pathToData, uniquePageList, removeItemList)
    
    # Transpose the surveys
    if "survey" in uniquePageList:
        surveyNameList = []
        for pageName, stimuliArgList in pageNameList[0]:
            if pageName == "survey":
                surveyName = stimuliArgList[0]
                surveyNameList.append(join(rootPath, surveyName + '.txt'))
        
        transpose_survey.transposeSurvey(join(pathToData, "survey"),
                                         surveyNameList, outputPath)
     
    # Transpose the rpt pages
    prominencePageList = ["prominence", "boundary", "boundary_and_prominence",
                          "syllable_marking"]
    for pageName in prominencePageList:
        if pageName in uniquePageList:
            transpose_rpt.transposeRPT(join(pathToData, pageName),
                                       txtPath, pageName, outputPath)
            
    choicePageList = ["media_choice", ]
    for pageName in choicePageList:
        if pageName in uniquePageList:
            transpose_choice.transposeChoice(join(pathToData, pageName),
                                             pageName,
                                             outputPath)


if __name__ == "__main__":

    description = "Verifies that the sequence file is well formed"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('test_name', action='store',
                        help=("The name of the root folder that stores the "
                              "test files"))
    parser.add_argument('sequence_fn', action='store',
                        help=("The sequence .txt file"))
    parser.add_argument('remove_duplicates_flag', action='store',
                        help=("Remove duplicate items?  (true/false)"))
    parser.add_argument('--remove_list', action='store', nargs='*',
                        help=("A list of stimuli names to remove from "
                              "consideration.  Typically, these are testing "
                              "or demonstration items.  List as many items "
                              "as needed after --remove_list, separated by "
                              "a space character"))
    try:
        cmdArgs = user_script_helper.runScriptLogic(parser)
    except user_script_helper.InteractiveModeException:
        _test_name = raw_input(("Enter the name of your test "
                                "(the root folder):\n"))
        _sequence_fn = raw_input("Enter the name of your sequence file:\n")
        _remove_duplicates_flag = raw_input("Remove duplicate items? "
                                            "(true/false)\n")
        _remove_items_flag = raw_input("Would you like to remove any items "
                                       "(e.g. sample/test items)? (yes/no):\n")
        if _remove_items_flag.lower() == 'yes':
            _remove_item_list = raw_input("Enter a list of stimuli names to "
                                          "remove (separated by a space):\n")
            _remove_item_list = _remove_item_list.split(" ")
        else:
            _remove_item_list = []
    else:
        _test_name = cmdArgs.test_name
        _sequence_fn = cmdArgs.sequence_fn
        _remove_duplicates_flag = cmdArgs.remove_duplicates_flag
        _remove_item_list = cmdArgs.remove_list
    
    if _remove_duplicates_flag.lower() == 'true':
        _remove_duplicates_flag = True
    elif _remove_duplicates_flag.lower() == 'false':
        _remove_duplicates_flag = False

    postProcessResults(_test_name, _sequence_fn, _remove_duplicates_flag,
                       _remove_item_list)
