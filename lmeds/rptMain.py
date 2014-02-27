#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import join
import ast

import cgi

import __main__

import html
import validation
import audio
import sequence
import loader
import pageTemplates
import constants
import survey



# First page (name page) + consentPage + instructionsPage + ?
#numExtraneousPages = 3

#CONSENT_PAGE = 1
#totalNumPages = loader.readGetNumItems()
#FINAL_PAGE = totalNumPages + numExtraneousPages








#def runCGI():
#
#    import cgitb
#    cgitb.enable()    
#
#    loader.initTextDict(textDictFN)
#
#    testSequence = sequence.TestSequence(sequenceFN)
#    
#    cgiForm = cgi.FieldStorage()
#    
#    # The user has not started the test
#    if not cgiForm.has_key("pageNumber"):
#        cookieTracker = 0 # This value is irrelevant but it must always increase
#                            # --if it does not, the program will suspect a refresh-
#                            #    or back-button press and end the test immediately
#        pageNum = 0 # Used for the progress bar
#        page = [('main', 0, ('login', [])),] # The initial state
#        userName = ""
#    
#    # Extract the information from the form
#    else:
#        pageNum, cookieTracker, page, userName = processForm(cgiForm, testSequence)
#        
#    
#    buildPage(pageNum, cookieTracker, page, userName, testSequence, sourceCGIFN)
#
#
#def debugCGI(page, pageNum=1, cookieTracker=True, userName="testing"):
#    
#    testSequence = sequence.TestSequence(sequenceFN)
#    loader.initTextDict(textDictFN)
#    buildPage(pageNum, cookieTracker, page, userName, testSequence, sourceCGIFN)


class WebSurvey(object):
    
    
    def __init__(self, surveyName, sequenceFN, languageFileFN, 
                 disableRefreshFlag, sourceCGIFN=None):
        
        self.surveyRoot = join(constants.rootDir, "tests", surveyName)
        self.wavDir = join(self.surveyRoot, "audio")
        self.txtDir = join(self.surveyRoot, "txt")
        self.outputDir = join(self.surveyRoot, "output")
        
        self.surveyName = surveyName
        self.sequenceFN = join(self.surveyRoot, sequenceFN)
        self.languageFileFN = join(self.surveyRoot, languageFileFN)
        
        self.disableRefreshFlag = disableRefreshFlag
        
        # The sourceCGIFN is the CGI file that was requested from the server
        # (basically the cgi file that started the websurvey)
        self.sourceCGIFN = None
        if sourceCGIFN == None:
            self.sourceCGIFN = os.path.split(__main__.__file__)[1]
#        self.sourceCGIFN = os.path.splitext(self.sourceCGIFN)
    
    
    def run(self):
        import cgitb
        cgitb.enable()    
    
        loader.initTextDict(self.languageFileFN)
    
        testSequence = sequence.TestSequence(self.sequenceFN)
        
        cgiForm = cgi.FieldStorage()
        
        # The user has not started the test
        if not cgiForm.has_key("pageNumber"):
            cookieTracker = 0 # This value is irrelevant but it must always increase
                                # --if it does not, the program will suspect a refresh-
                                #    or back-button press and end the test immediately
            pageNum = 0 # Used for the progress bar
            page = [('main', 0, ('login', [], {})),] # The initial state
            userName = ""
        
        # Extract the information from the form
        else:
            pageNum, cookieTracker, page, userName = self.processForm(cgiForm, testSequence)
            
        
        self.buildPage(pageNum, cookieTracker, page, userName, testSequence, self.sourceCGIFN)
    
    
    def runDebug(self, page, pageNum=1, cookieTracker=True, userName="testing"):
        
        testSequence = sequence.TestSequence(self.sequenceFN)
        loader.initTextDict(self.languageFileFN)
        self.buildPage(pageNum, cookieTracker, page, userName, testSequence, self.sourceCGIFN)


    def processForm(self, form, testSequence):
        '''
        Get the page number and user info from the previous page; serialize user data
        '''
        
        userName = ""
        
        
        cookieTracker = int(form["cookieTracker"].value)
        cookieTracker += 1
        
        pageNum = int(form["pageNumber"].value)
        pageNum += 1
        
        lastPage = ast.literal_eval(form["page"].value)
        subroutine = lastPage[-1][0]
        taskType = lastPage[-1][2][0]
        
        # This is the default next page, but in the code below we will see
        #    if we need to override that decision
        sequenceTitle, nextPage = testSequence.getNextPage(lastPage)
        
        # If a user name text control is on the page, extract the user name from it
        if form.has_key("user_name_init"):
            
            userName = form["user_name_init"].value
            userName = userName.strip()
            
            # Return to the login page without setting the userName if there is 
            # already data associated with that user name
            outputFN = join(self.outputDir, sequenceTitle, userName+".txt")
            nameAlreadyExists = os.path.exists(outputFN)
            
            if nameAlreadyExists or userName == "":
                nextPage = lastPage[:-1] + [(subroutine, 0, ('login_bad_user_name', [userName,], {}))]
                pageNum -= 1 # We wrongly guessed that we would be progressing in the test
                
        # Otherwise, the user name, should be stored in the form    
        elif form.has_key("user_name"):
            userName = form["user_name"].value    
        
        # Serialize all variables
        self.serializeResults(form, lastPage, userName, sequenceTitle)
    
        # Go to a special end state if the user does not consent to the study
        if taskType == 'consent':
            if form['radio'].value == 'dissent':
                nextPage = [(subroutine, 0, ('consent_end', [], {}))]
    #            print open("../html/optOut.html", "r").read()
    
    
        return pageNum, cookieTracker, nextPage, userName
    
    
    def getNumOutputs(self, testType, fnFullPath):
        numOutputs = 0 # All non-trial pages do not have any outputs
        if testType in ['prominence', 'boundary', 'oldProminence',
                        'oldBoundary', 'boundaryAndProminence']:
            wordList = loader.loadTxt(fnFullPath)
            numOutputs = 0
            for line in wordList:
                numOutputs += len(line.split(" "))
            
            if testType == 'oldBoundary':
                numOutputs -= 1
                
            if testType == 'boundaryAndProminence':
                numOutputs *= 2
        
        elif testType in ['axb',]:
            numOutputs = 2 # A, B
            
        elif testType in ['abn',]:
            numOutputs = 3 # A, B, N
            
        return numOutputs
    
    
    def buildPage(self, pageNum, cookieTracker, page, userName, testSequence, sourceCGIFN):  
        html.printCGIHeader(cookieTracker, self.disableRefreshFlag)
    
        subroutine, subPageNum, task = page[-1]
    #    print page
        testType, argList, kargDict = task
    
        # Defaults
        embedTxt = audio.generateEmbed(self.wavDir, [])
        validateText = validation.getValidationForPage(testType)
        
        # Estimate our current progress (this doesn't work well if the user
        #    can jump around)
        totalNumPages = len(testSequence.iterate())
        percentComplete = int(100*(pageNum)/(totalNumPages))
        
        htmlTxt, pageTemplateFN, updateDict = pageTemplates.getPageTemplates(self)[testType](*argList, **kargDict)
        
        try:
            name = argList[0]
            txtFN = join(self.txtDir, name+".txt")
            numItems = self.getNumOutputs(testType, txtFN)
        except IndexError:
            numItems = 0
        
        # Also HACK
        processSubmitHTML = html.getProcessSubmitHTML(testType)
        if 'embed' in updateDict.keys():
            updateDict['embed'] += processSubmitHTML
        else:
            embedTxt += processSubmitHTML
        
    #    print cookieTracker, pageNum, testType, argList
        
        # HACK
        if testType == 'boundaryAndProminence':
            formHTML = html.formTemplate2
        else:
            formHTML = html.formTemplate
            
        progressBarHTML = html.getProgressBar()  % {'percentComplete': percentComplete,
                                                      'percentUnfinished': 100 - percentComplete,}
                
        htmlDict = { 
                     'html':htmlTxt,
                     'pageNumber':pageNum,
                     'cookieTracker':cookieTracker,
                     'page':page,
                     'user_name':userName,
                     'validate':validateText,
                     'embed':embedTxt,
                     'program_title':constants.softwareName,
                     'source_cgi_fn':sourceCGIFN,
                     'num_items':numItems,
                     'submit_button_text':loader.getText('continue button')
                                     }
        
        
        pageTemplate = open(pageTemplateFN, "r").read()
        pageTemplate %= {'form':formHTML,
                         'progressBar': progressBarHTML,
                         'pressBackWarning': loader.getText('back button warning')}
        htmlDict.update(updateDict)
    
        htmlOutput = pageTemplate % htmlDict
        
        print htmlOutput.encode('utf-8')
    
    
    def _getLeafSequenceName(self, page):
        '''
        Sequences can contain many subsequences--this fetches the leaf sequence
        '''
        
        if type(page[-1]) == type(()):
            retValue = self._getLeafSequenceName(page[-1])
        else:
            retValue = page[0]
            
        return retValue 
    
    
    def getoutput(self, key, form):
        '''
        
        Output from the cgi form is the name of the indices that were marked positive.
        Here we use the convention that checkboxes are ordered and named as such
        (e.g. "1", "2", "3", etc.).
        
        This code converts this list into the full list of checked and unchecked
        boxes, where the index of the item in the row contains the value of the 
        corresponding checkbox
        e.g. for 'Tom saw Mary' where each word can be selected by the user,
        the sequence [0, 0, 1] would indicate that 'Mary' was selected and 'Tom' 
        and 'saw' were not.
        '''
        numItems = int(form.getvalue('num_items'))
        
        # Contains index of all of the positively marked items (ignores unmarked items)
        outputList = form.getlist(key)
    
        # Assume all items unmarked
        retList = ["0" for i in xrange(numItems)]
        
        # Mark positively marked items
        for i in outputList:
            retList[int(i)] = "1"
        
        return key, ",".join(retList)
    
    
    def serializeResults(self, form, page, userName, sequenceTitle):
        
        # The arguments to the task hold the information that distinguish
        #    this trial from other trials
        currentPage = page[-1]
        currentTaskTuple = currentPage[2]
        taskName = currentTaskTuple[0]
        taskArguments = currentTaskTuple[1] 
        taskArgumentStr = ";".join(taskArguments)

        numPlays1 = form.getvalue('audioFilePlays0')
        numPlays2 = form.getvalue('audioFilePlays1')
        taskDuration = form.getvalue('task_duration')
        
        if taskName == "survey":
            outputList = self.getOutputForSurvey(form, taskArguments[0])
        elif taskName == "consent":
            outputList = self.getOutputForConsent(form)
        else:
            outputList = self.getOutputForTask(form, taskName)
        
        # Serialize data
        for key, value in outputList:
            experimentOutputDir = join(self.outputDir, sequenceTitle)
            if not os.path.exists(experimentOutputDir):
                os.mkdir(experimentOutputDir)
                
    #         outputDir = join(experimentOutputDir, key)
    #         if not os.path.exists(outputDir):
    #             os.mkdir(outputDir)
                
            outputFN = join(experimentOutputDir, "%s.csv" % (userName))
            fd = open(outputFN, "a")
            fd.write( "%s,%s,%s,%s,%s;,%s\n" % (key,taskArgumentStr,numPlays1, numPlays2, taskDuration, value))    
            fd.close()


    def getOutputForTask(self, form, taskName):
        # Identify the keys associated with data that we want to serialize
        keyList = []
        if 'prominence' == taskName:
            keyList.append('p')
        if 'boundary' == taskName:
            keyList.append('b')
        if 'axb' == taskName:
            keyList.append('axb')
        if 'abn' == taskName:
            keyList.append('abn')
        if 'same_different' == taskName:
            keyList.append('same_different')
            
        # We should not distinguish between different kinds of keys
        # -- all checkboxes on a page should be the same 
        # -- (I can't see the reason to do otherwise)
        if 'boundary_and_prominence' == taskName:
            keyList.append('b_and_p')
        
        
        
    
        
        # At the moment, only allow a single key (or none)
        assert(len(keyList) <= 1)
        outputList = []
        for key in keyList:
            outputList.append(self.getoutput(key, form))
    #         open('../outputTest.txt', "a").write(str(outputList))

        return outputList
    
    
    def getOutputForSurvey(self, form, surveyName):
        surveyItemList = survey.parseSurveyFile(join(self.surveyRoot, surveyName + ".txt"))
        
        tmpList = []
        k = 0
        for j, item in enumerate(surveyItemList):
            
            
            for i, currentItem in enumerate(item.widgetList):
                itemType, argList = currentItem
                
                
                value = form.getvalue(str(k))
                
                if not value:
                    value = ""
                    if itemType in ["Choice", "Item_List", "Choicebox"]:
                        value = ","*(len(argList)-1) # 1 comma between every element
                else:
                    
                    # Remove newlines (because each newline is a new data entry)
                    if itemType == "Multiline_Textbox":
                        value = value.replace(",", "") # Remove commas (because saved as a CSV file)
                        newlineChar = utils.detectLineEnding(value)
                        if newlineChar != None:
                            value = value.replace(newlineChar, " - ") 
                    
                    if itemType in ["Choice", "Choicebox"]:
                        if itemType == "Choice":
                            index = argList.index(value)
                        elif itemType == "Choicebox":
                            index = int(value)
                            
                        valueList = ["0" for x in xrange(len(argList))]
                        valueList[index] = "1"
                        value = ",".join(valueList)
                        
                    elif itemType in ["Item_List"]:
                        indexList = [argList.index(subVal) for subVal in value]
                        valueList = ["1" if i in indexList else "0" for i in xrange(len(argList))]
                        value = ",".join(valueList)
                    
                tmpList.append(value)
                k += 1
        
#         tmpList = outputList
        
        return [("survey", ",".join(tmpList)),]
            
    
    def getOutputForConsent(self, form):
        didConsent = form.getvalue("radio")
        
        timestamp = datetime.datetime.now().isoformat()
        if didConsent == "consent":
            returnTxt = "User consented to participate in experiment on %s"
        else:
            returnTxt = "User declined consent to participate in experiment on %s"

        return [("consent", returnTxt % timestamp),]
    

if __name__ == "__main__":
    survey = WebSurvey("files_perceptionOfDiscourseMeaning", "sequence.txt", "english", True)
#    survey.run()
    survey.runDebug([('main', 1, ('axb', ['apples', 'water', 'apples']))],)
   
#     runCGI()
#     
#    print "hello"
    
    
    