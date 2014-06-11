'''
Created on Feb 28, 2014

@author: tmahrt
'''

from lmeds.pages import simpleExperimentPages
from lmeds.pages import boundaryPages
from lmeds.pages import corePages


class ReservedWordException(Exception):
    
    
    def __str__(self):
        return "'webSurvey' is a reserved word and cannot be used in dictionary"
    
    
    
def loadPage(webSurvey, pageName, args=None, kargs=None):
    
    if args == None:
        args = []
        
    if kargs == None:
        kargs = {}

    if 'webSurvey' in kargs.keys():
        raise ReservedWordException()
    
    kargs['webSurvey'] = webSurvey

    
    pageClassList = [
                     simpleExperimentPages.AXBPage,
                     simpleExperimentPages.ABPage,
                     simpleExperimentPages.ABNPage,
                     simpleExperimentPages.SameDifferentPage,
                     simpleExperimentPages.SurveyPage,
                     simpleExperimentPages.AudioListPage,
                     simpleExperimentPages.MemoryPage,
                     simpleExperimentPages.FillInTheBlankPage,
                     simpleExperimentPages.SameDifferentBeepPage,
                     simpleExperimentPages.SameDifferentStream,
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

    pageDict = dict((pageClass.sequenceName, pageClass) for pageClass in pageClassList)

    
    return pageDict[pageName](*args, **kargs)
    
    

