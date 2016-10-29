#!/usr/bin/env python
'''
Created on Aug 9, 2015

@author: tmahrt
'''
import os
import sys
import math
import argparse
from os.path import dirname, abspath, join

os.chdir(dirname(dirname(abspath(__file__))))
sys.path.append("..")

from lmeds.lmeds_io import user_response
from lmeds.lmeds_io import sequence
from lmeds.utilities import utils
from lmeds.utilities import user_script_helper
from lmeds.utilities import constants


def printTestDuration(path):
    allTime = []
    for fn in utils.findFiles(path, filterExt=".csv"):
        timeStrList = [rowTuple[2].split(",")[-2] for rowTuple in
                       user_response.loadUserResponse(join(path, fn))]
        timeList = []
        for timeStamp in timeStrList:
            try:
                minutes, seconds = timeStamp.split(':')
            except ValueError:
                continue
            seconds = int(minutes) * 60 + float(seconds)
            minutes = seconds / 60.0
            timeList.append(minutes)
            
        totalTime = sum(timeList)
        allTime.append(totalTime)
        
        print("%s, %f" % (fn, totalTime))
    
    meanTime = sum(allTime) / len(allTime)
    print("Mean: %f" % meanTime)
    
    timeDeviationList = [(time - meanTime) ** 2 for time in allTime]
    stDev = math.sqrt(sum(timeDeviationList) / len(allTime))
    print("Standard Deviation: %f" % stDev)
    
if __name__ == "__main__":
    
    description = "Prints how long each user spent on an experiment"
    parser = argparse.ArgumentParser(description=description)
    
    parser.add_argument('root_folder', action='store',
                        help=("The name of the root folder that stores the "
                              "test files"))
    parser.add_argument('sequence_fn', action='store',
                        help=("The sequence .txt file"))
    
    try:
        cmdArgs = user_script_helper.runScriptLogic(parser)
    except user_script_helper.InteractiveModeException:
        _root_folder = raw_input("Enter the name of your experiment "
                                 "(the root folder in /tests/):\n")
        _sequence_fn = raw_input("Enter the name of your sequence file:\n")
    else:
        _root_folder = cmdArgs.root_folder
        _sequence_fn = cmdArgs.sequence_fn
    
    rootPath = join(constants.rootDir, "tests", _root_folder)
    tmpSequence = sequence.TestSequence(None, join(rootPath, _sequence_fn))
    fullPath = join(rootPath, "output", tmpSequence.sequenceTitle)
    printTestDuration(fullPath)
