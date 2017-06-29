#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import join

import cgi

import __main__

import io

from lmeds.pages import factories
from lmeds.code_generation import html
from lmeds.code_generation import audio
from lmeds.lmeds_io import sequence
from lmeds.lmeds_io import loader
from lmeds.utilities import constants
from lmeds.utilities import utils

# Strings used by all web surveys
TXT_KEY_LIST = ["continue_button", "metadata_description",
                "back_button_warning"]
# Common strings not used directly by WebSurvey
TXT_EXTERNAL_KEY_LIST = ["progress", "loading_progress"]
TXT_KEY_LIST.extend(TXT_EXTERNAL_KEY_LIST)

jqueryCode = ('''<script type="text/javascript" src='''
              '''"//code.jquery.com/jquery-1.11.0.min.js"></script>\n'''
              '''<script type="text/javascript">\n'''
              '''if (typeof jQuery == 'undefined') {\n'''
              '''document.write(unescape("%3Cscript src='''
              ''''../html/jquery-1.11.0.min.js' '''
              '''type='text/javascript'%3E%3C/script%3E"));'''
              '''\n}\n'''
              '''</script>\n'''
              '''<script type="text/javascript" src='''
              '''"../html/lmeds-audio.js"></script>\n'''
              '''<script type="text/javascript" src='''
              '''"../html/lmeds-utils.js"></script>\n'''
              '''<script type="text/javascript" src='''
              '''"../html/lmeds-forms.js"></script>\n'''
              '''<script type="text/javascript" src='''
              '''"../html/b-p-scores.js"></script>\n'''
              )


class WebSurvey(object):
    
    def __init__(self, surveyName, sequenceFN, languageFileFN,
                 disableRefreshFlag, sourceCGIFN=None, audioExtList=None,
                 videoExtList=None, allowUsersToRelogin=False,
                 individualSequences=False
                 ):
        
        self.htmlDir = constants.htmlDir
        self.htmlSnippetsDir = constants.htmlSnippetsDir
        
        self.surveyRoot = join(constants.rootDir, "tests", surveyName)
        self.wavDir = join(self.surveyRoot, "audio_and_video")
        self.txtDir = join(self.surveyRoot, "txt")
        self.imgDir = join(self.surveyRoot, "imgs")
        self.outputDir = join(self.surveyRoot, "output")
        self.allowUsersToRelogin = allowUsersToRelogin
        self.individualSequences = individualSequences
        
        self.surveyName = surveyName
        self.sequenceFN = join(self.surveyRoot, sequenceFN)
        self.testSequence = sequence.TestSequence(self, self.sequenceFN)
        
        if languageFileFN is not None:
            languageFileFN = join(self.surveyRoot, languageFileFN)
        self.languageFileFN = languageFileFN
        
        if audioExtList is None:
            audioExtList = [".ogg", ".mp3"]
        self.audioExtList = audioExtList
        
        if videoExtList is None:
            videoExtList = [".ogg", ".mp4"]
        self.videoExtList = videoExtList
        
        if self.languageFileFN is None:
            self.langDict = loader.EmptyDict()
        else:
            self.langDict = loader.TextDict(self.languageFileFN)
        
        self.disableRefreshFlag = disableRefreshFlag
        
        self.textDict = self.langDict.batchGetText(TXT_KEY_LIST)
        
        # The sourceCGIFN is the CGI file that was requested from the server
        # (basically the cgi file that started the websurvey)
        self.sourceCGIFN = None
        if sourceCGIFN is None:
            self.sourceCGIFN = os.path.split(__main__.__file__)[1]
    
    def run(self, cgiForm=None):
        
        # Imported here to prevent it from being run in runDebug?
        if cgiForm is None:
            import cgitb
            cgitb.enable()
            
            cgiForm = cgi.FieldStorage(keep_blank_values=True)
        
        # The user has not started the test
        if "pageNumber" not in cgiForm:
            # This value is irrelevant but it must always increase
            # --if it does not, the program will suspect a refresh-
            # or back-button press and end the test immediately
            cookieTracker = 0
            pageNum = 0  # Used for the progress bar
            page = self.testSequence.getPage(0)
            userName = ""
        
        # Extract the information from the form
        else:
            formTuple = self.processForm(cgiForm)
            pageNum, cookieTracker, page, userName = formTuple
        
        self.buildPage(pageNum, cookieTracker, page, userName,
                       self.testSequence, self.sourceCGIFN)
    
    def runDebug(self, page, pageNum=1, cookieTracker=True,
                 userName="testing"):
        
        testSequence = sequence.TestSequence(self, self.sequenceFN)
        self.buildPage(pageNum, cookieTracker, page, userName,
                       testSequence, self.sourceCGIFN)

    def processForm(self, form):
        '''
        Get page number + user info from previous page; serialize user data
        '''
        
        userName = ""
        
        cookieTracker = int(form["cookieTracker"].value)
        cookieTracker += 1
        
        pageNum = int(form["pageNumber"].value)
        lastPageNum = pageNum
        
        # This is the default next page, but in the code below we will see
        # if we need to override that decision
        pageNum += 1
        sequenceTitle = self.testSequence.sequenceTitle
        nextPage = None
        
        # If a user name text control is on the page,
        # extract the user name from it
        if "user_name_init" in form:
            
            userName = utils.decodeUnicode(form["user_name_init"].value)
            userName = userName.strip()
            
            # Return to the login page without setting the userName if there is
            # already data associated with that user name
            outputFN = join(self.outputDir, sequenceTitle, userName + ".csv")
            nameAlreadyExists = (os.path.exists(outputFN))
            
            if nameAlreadyExists or userName == "":
                
                # Is relogging in allowed?
                if self.allowUsersToRelogin is True:
                    # Find the last page of saved user data
                    # If the user is coming back, the 'login' page will
                    # reappear on their output file
                    with io.open(outputFN, "r", encoding='utf-8') as fd:
                        pageLineList = fd.readlines()
                    while len(pageLineList) > 0:
                        pageLine = pageLineList.pop(-1)
                        pageArgList = pageLine.split(";,")[0].split(",")
                        if pageArgList[0] == "login":
                            continue
                        
                        pageNum = int(pageArgList[-1]) + 1
                        break
                    
                # If not, throw an error page
                else:
                    nextPage = factories.loadPage(self, "login_bad_user_name",
                                                  [userName, ], {})
                    # We wrongly guessed that we would be progressing
                    pageNum -= 1
        
        # Otherwise, the user name, should be stored in the form
        elif "user_name" in form:
            userName = utils.decodeUnicode(form["user_name"].value)
        
        self._testSequenceOverride(userName)
        
        # Get last page info
        lastPage = self.testSequence.getPage(lastPageNum)
        sequenceTitle = self.testSequence.sequenceTitle
            
        # Serialize all variables
        self.serializeResults(form, lastPage, lastPageNum,
                              userName, sequenceTitle)
        
        # Go to a special end state if the user does not consent to the study
        if lastPage.pageName == 'consent':
            if form['radio'].value == 'dissent':
                nextPage = factories.loadPage(self, "consent_end")
        
        # Go to a special end state if the user cannot play audio files
        if lastPage.pageName == 'media_test':
            if form['radio'].value == 'dissent':
                nextPage = factories.loadPage(self, "media_test_end", [], {})
    
        if nextPage is None:
            nextPage = self.testSequence.getPage(pageNum)
        
        return pageNum, cookieTracker, nextPage, userName
    
    def buildPage(self, pageNum, cookieTracker, page, userName,
                  testSequence, sourceCGIFN):
        
        self._testSequenceOverride(userName)
            
        html.printCGIHeader(cookieTracker, self.disableRefreshFlag)
        
        validationTemplate = ('// Validate page form before submitting\n'
                              'function validateForm()\n{\n%s\n}\n\n')
        validateText = validationTemplate % page.getValidation()
        
        # Defaults
        jsHeader = jqueryCode
        embedTxt = jsHeader
        
        # Estimate our current progress (this doesn't work well if the user
        #    can jump around)
        totalNumPages = float(len(testSequence.testItemList))
        percentComplete = int(100 * (pageNum) / (totalNumPages - 1))
        
        htmlTxt, pageTemplateFN, updateDict = page.getHTML()
        loadingProgressTxt = self.textDict["loading_progress"]
        htmlTxt = html.getLoadingNotification(loadingProgressTxt) + htmlTxt
        testType = page.pageName
        
        numItems = page.getNumOutputs()
        
        # Also HACK
        processSubmitHTML = page.getProcessSubmitFunctions()
        
        # HACK
        if testType == 'boundary_and_prominence':
            formHTML = html.formTemplate2
        else:
            formHTML = html.formTemplate
        # -*- coding: utf-8 -*-
        
        submitWidgetList = []
        if page.submitProcessButtonFlag:
            continueButtonTxt = self.textDict['continue_button']
            submitButtonHTML = html.submitButtonHTML % continueButtonTxt
            submitWidgetList.append(('widget', "submitButton"),)
        else:
            submitButtonHTML = ""
        
        submitWidgetList.extend(page.nonstandardSubmitProcessList)

        # Javascript to run once the page has loaded
        runOnLoad = "document.myTimer = new Timer();"
        submitAssociation = html.constructSubmitAssociation(submitWidgetList)
        runOnLoad += submitAssociation
        
        if page.getNumAudioButtons() > 0:
#             audioLoadingJSCmd = audio.generateEmbed(self.wavDir, [],
#                                                     self.audioExtList,
#                                                     "audio")
#             runOnLoad += audioLoadingJSCmd
            runOnLoad += audio.loadAudioSnippet
            pushTemplate = "audioLoader.minPlayFuncList.push(%s)\n"
            try:
                funcList = page.playOnMinList
            except AttributeError:
                pass
            else:
                for func in funcList:
                    runOnLoad += pushTemplate % func
            
            for flagName in ["silenceFlag", "listenPartial"]:
                try:
                    boolVal = getattr(page, flagName)
                except AttributeError:
                    pass
                else:
                    txtVal = "true" if boolVal else "false"
                    runOnLoad += ("audioLoader.%s = %s;" % (flagName, txtVal))
        
        try:
            runOnLoad += page.runOnLoad
        except AttributeError:
            pass
        
        processSubmitHTML += html.runOnPageLoad % runOnLoad
        processSubmitHTML += validateText
        
        scriptFmt = '<script type="text/javascript">\n%s\n</script>'
        if 'embed' in updateDict.keys():
            
            # Add page-specific constraints on audio playback if
            # this page has audio
            if "audioLoader" in updateDict["embed"]:
                minMaxTxt = ""
                try:
                    minMaxTxt += ("audioLoader.minNumPlays = %s;\n" %
                                  page.minPlays)
                except AttributeError:
                    pass
                try:
                    minMaxTxt += ("audioLoader.maxNumPlays = %s;\n" %
                                  page.maxPlays)
                except AttributeError:
                    pass
                try:
                    minMaxTxt += ("audioLoader.numAudioButtons = %s;\n" %
                                  page.numAudioButtons)
                except AttributeError:
                    pass

                minMaxTxt += ("audioLoader.numUniqueSoundFiles = "
                              "countUnique(audioLoader.audioList);\n")
                updateDict['embed'] += minMaxTxt
            
            tmpEmbed = scriptFmt % (processSubmitHTML + updateDict['embed'])
            updateDict['embed'] = jqueryCode + tmpEmbed
        else:
            embedTxt += scriptFmt % processSubmitHTML
            
        progressBarDict = {'percentComplete': percentComplete,
                           'percentUnfinished': 100 - percentComplete, }
        progressTxt = self.textDict["progress"]
        progressBarHTML = html.getProgressBar(progressTxt) % progressBarDict

        metaDescription = self.textDict["metadata_description"]
                
        audioPlayTrackingHTML = ""
        for i in range(page.getNumAudioButtons()):
            audioPlayTrackingHTML += html.audioPlayTrackingTemplate % {"id": i}
                
        htmlDict = {'html': htmlTxt,
                    'pageNumber': pageNum,
                    'cookieTracker': cookieTracker,
                    'page': page,
                    'user_name': userName,
                    'embed': embedTxt,
                    'metadata_description': metaDescription,
                    'websiteRootURL': constants.rootURL,
                    'program_title': constants.softwareName,
                    'source_cgi_fn': sourceCGIFN,
                    'num_items': numItems,
                    'audio_play_tracking_html': audioPlayTrackingHTML,
                    'submit_button_slot': submitButtonHTML,
                    }
        
        backButtonTxt = self.textDict['back_button_warning']
        with io.open(pageTemplateFN, "r", encoding='utf-8') as fd:
            pageTemplate = fd.read()
        pageTemplate %= {'form': formHTML,
                         'progressBar': progressBarHTML,
                         'pressBackWarning': backButtonTxt}
        htmlDict.update(updateDict)
    
        htmlOutput = pageTemplate % htmlDict
        
        utils.outputUnicode(htmlOutput)
    
    def _testSequenceOverride(self, userName):
        '''
        Override the test sequence
        
        This is done only when we're using individual sequences
        '''

        if self.individualSequences is True:
            if userName != "" and self.sequenceFN != userName + ".txt":
                testSequence = sequence.TestSequence(self,
                                                     self.sequenceFN,
                                                     userName)
                self.testSequence = testSequence
    
    def _getLeafSequenceName(self, page):
        '''
        Sequences can contain many subsequences--this fetches the leaf sequence
        '''
        
        if isinstance(page[-1], constants.list):
            retValue = self._getLeafSequenceName(page[-1])
        else:
            retValue = page[0]
            
        return retValue
    
    def getoutput(self, key, form):
        '''
        
        Output from the cgi form is the name of the indices that were marked
        positive. Here we use the convention that checkboxes are ordered and
        named as such (e.g. "1", "2", "3", etc.).
        
        This code converts this list into the full list of checked and
        unchecked boxes, where the index of the item in the row contains
        the value of the corresponding checkbox
        e.g. for 'Tom saw Mary' where each word can be selected by the user,
        the sequence [0, 0, 1] would indicate that 'Mary' was selected and
        'Tom' and 'saw' were not.
        '''
        numItems = int(form.getvalue('num_items'))
        
        # Contains index of all of the positively marked items
        # (ignores unmarked items)
        outputList = form.getlist(key)
    
        # Assume all items unmarked
        retList = ["0" for i in range(numItems)]
        
        # Mark positively marked items
        for i in outputList:
            retList[int(i)] = "1"
        
        return key, ",".join(retList)
    
    def serializeResults(self, form, page, pageNum, userName, sequenceTitle):
        
        # The arguments to the task hold the information that distinguish
        #    this trial from other trials
        
        taskArgumentList = self.testSequence.getPageStr(pageNum)[1]
        taskArgumentStr = utils.recNestedListToStr(taskArgumentList)

        numPlays1 = form.getvalue('audioFilePlays0')
        numPlays2 = form.getvalue('audioFilePlays1')
        taskDuration = form.getvalue('task_duration')
        
        key = page.pageName
        value = page.getOutput(form)
        
        # Serialize data
        experimentOutputDir = join(self.outputDir, sequenceTitle)
        if not os.path.exists(experimentOutputDir):
            os.mkdir(experimentOutputDir)
            
        outputFN = join(experimentOutputDir, "%s.csv" % (userName))
        
        outputStr = u"%s,%s,%s,%s,%s,%s;,%s\n" % (key, taskArgumentStr,
                                                  numPlays1, numPlays2,
                                                  taskDuration, pageNum,
                                                  value)

        with io.open(outputFN, "a", encoding="utf-8") as fd:
            fd.write(outputStr)
