'''
Created on Apr 29, 2016

@author: Tim
'''

import base_demo

survey = base_demo.survey

for i in range(survey.testSequence.getNumPages()):
    page = survey.testSequence.getPage(i)
    survey.buildPage(i, "", page, "no_name", survey.testSequence,
                     survey.sourceCGIFN)
