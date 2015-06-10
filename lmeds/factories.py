'''
Created on Feb 28, 2014

@author: tmahrt
'''

from lmeds.pages import simpleExperimentPages
from lmeds.pages import boundaryPages
from lmeds.pages import corePages
from lmeds.pages import axb_pages


class ReservedWordException(Exception):
    
    def __str__(self):
        return ("'webSurvey' is a reserved word and cannot be "
                "used in dictionary"
                )


def loadPage(webSurvey, pageName, args=None, kargs=None):
    
    if args is None:
        args = []
        
    if kargs is None:
        kargs = {}

    if 'webSurvey' in kargs.keys():
        raise ReservedWordException()
    
    kargs['webSurvey'] = webSurvey
    
    pageClassList = [axb_pages.AXBPage,
                     axb_pages.ABPage,
                     axb_pages.ABNPage,
                     axb_pages.ABNOneAudio,
                     axb_pages.ABNTwoAudio,
                     axb_pages.ABNThreeAudio,
                     axb_pages.SameDifferentPage,
                     simpleExperimentPages.SurveyPage,
                     simpleExperimentPages.AudioListPage,
                     simpleExperimentPages.AudioWithResponsePage,
                     simpleExperimentPages.TextResponsePage,
                     simpleExperimentPages.MemoryPage,
                     simpleExperimentPages.FillInTheBlankPage,
                     axb_pages.SameDifferentBeepPage,
                     axb_pages.SameDifferentStream,
                     corePages.LoginPage,
                     corePages.LoginErrorPage,
                     corePages.EndPage,
                     corePages.AudioTestPage,
                     corePages.AudioTestEndPage,
                     corePages.ConsentPage,
                     corePages.ConsentEndPage,
                     corePages.TextPage,
                     corePages.TextAndAudioPage,
                     boundaryPages.BoundaryAndProminencePage,
                     boundaryPages.BoundaryPage,
                     boundaryPages.ProminencePage,
                     ]

    pageDict = dict((pageClass.sequenceName, pageClass)
                    for pageClass in pageClassList)
    
    return pageDict[pageName](*args, **kargs)
