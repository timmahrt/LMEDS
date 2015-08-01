'''
Created on Feb 28, 2014

@author: tmahrt
'''

from lmeds.pages import assorted_experiment_pages
from lmeds.pages import boundary_pages
from lmeds.pages import core_pages
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
                     assorted_experiment_pages.SurveyPage,
                     assorted_experiment_pages.AudioListPage,
                     assorted_experiment_pages.AudioWithResponsePage,
                     assorted_experiment_pages.TextResponsePage,
                     assorted_experiment_pages.MemoryPage,
                     assorted_experiment_pages.FillInTheBlankPage,
                     axb_pages.SameDifferentBeepPage,
                     axb_pages.SameDifferentStream,
                     core_pages.LoginPage,
                     core_pages.LoginErrorPage,
                     core_pages.EndPage,
                     core_pages.AudioTestPage,
                     core_pages.AudioTestEndPage,
                     core_pages.ConsentPage,
                     core_pages.ConsentEndPage,
                     core_pages.TextPage,
                     core_pages.TextAndAudioPage,
                     boundary_pages.BoundaryAndProminencePage,
                     boundary_pages.BoundaryPage,
                     boundary_pages.ProminencePage,
                     ]

    pageDict = dict((pageClass.pageName, pageClass)
                    for pageClass in pageClassList)
    
    return pageDict[pageName](*args, **kargs)
