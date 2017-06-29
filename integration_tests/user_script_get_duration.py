'''
Created on Apr 29, 2016

@author: Tim
'''

from os.path import join

import base_demo
from lmeds.user_scripts import get_test_duration
from lmeds.lmeds_io import sequence
from lmeds.utilities import constants

survey = base_demo.survey

rootPath = join(constants.rootDir, "tests", "lmeds_demo")
tmpSequence = sequence.TestSequence(None, join(rootPath, "sequence.txt"))
fullPath = join(rootPath, "output", tmpSequence.sequenceTitle)
get_test_duration.printTestDuration(fullPath)
