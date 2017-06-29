'''
Created on Mar 1, 2014

@author: tmahrt

These pages define pages used for rapid prosody transcription.
'''

import os
from os.path import join

from lmeds.code_generation import html
from lmeds.code_generation import audio
from lmeds.utilities import constants
from lmeds.utilities import utils
from lmeds.lmeds_io import loader
from lmeds.pages import abstract_pages


def _doBreaksOrProminence(testType, wordIDNum, audioNum, name, textNameStr,
                          audioLabel, sentenceList, presentAudioFlag, token,
                          syllableDemarcator):
    '''
    This is a helper function.  It does not construct a full page.
    
    Can be used to prepare text for prominence OR boundary annotation
    (or both if called twice and aggregated).
    '''
    
    htmlTxt = ""
    
    instrMsg = ("%s<br /><br />\n\n" % textNameStr)
    htmlTxt += html.makeWrap(instrMsg)
    
    if presentAudioFlag is True:
        htmlTxt += audio.generateAudioButton(name, audioNum, audioLabel, False)
        htmlTxt += "<br /><br />\n\n"
    else:
        htmlTxt += "<br /><br />\n\n"
    
    sentenceListTxtList = []
    for sentence in sentenceList:
        if '<' in sentence:  # HTML check
            sentenceListTxtList.append(sentence)
        else:
            wordList = sentence.split(" ")
            
            tmpHTMLTxt = ""
            if syllableDemarcator is not None:
                wordList = [word.split(syllableDemarcator)
                            for word in wordList]
                for syllableList in wordList:
                    wordHTMLTxt = ""
                    for syllable in syllableList:
                        wordHTMLTxt += _makeTogglableWord(testType, syllable,
                                                          wordIDNum, token,
                                                          "syllable")
                        wordIDNum += 1
                        wordHTMLTxt += syllableDemarcator
                    
                    # Syllables are separated by a demarcator.  Words by
                    # spaces.  Here, remove the final demarcator and add a
                    # newline (interpreted as a space in HTML).
                    wordTemplate = '<span class="rptWordPadding">%s</span>\n'
                    tmpHTMLTxt += wordTemplate % wordHTMLTxt[:-1]
            else:
                for word in wordList:
                    # If a word is an HTML tag, it isn't togglable.
                    # Otherwise, it is
                    tmpHTMLTxt += _makeTogglableWord(testType, word,
                                                     wordIDNum, token,
                                                     "word")
                    wordIDNum += 1

            sentenceListTxtList.append(tmpHTMLTxt)
    
    newTxt = "<br /><br />\n\n".join(sentenceListTxtList)
            
    htmlTxt += newTxt
            
    return htmlTxt, wordIDNum


def _makeTogglableWord(testType, word, idNum, boundaryToken, labelClass):
    
    tokenTxt = ""
    if boundaryToken is not None:
        tokenTxt = """<span class="hidden">%s</span>""" % boundaryToken
    
    htmlTxt = ('<label for="%(idNum)d" class="%(class)s">'
               '<input type="checkbox" name="%(testType)s" id="%(idNum)d"'
               'value="%(idNum)d"/>'
               '%(word)s' + tokenTxt)
    
    if labelClass == "word":
        htmlTxt += "\n"
    
    htmlTxt += '</label>'

    return htmlTxt % {"testType": testType, "word": word, "idNum": idNum,
                      "class": labelClass}


def _getTogglableWordEmbed(page):
    
    # Add javascript that checks user markings
    minErrMsg = ""
    maxErrMsg = ""
    minMaxErrMsg = ""
    if page.minNumSelected != -1 or page.maxNumSelected != -1:
        if page.minNumSelected != -1:
            minErrMsg = page.textDict['pbMinSelectedErrorMsg']
            minErrMsg %= page.minNumSelected
        if page.maxNumSelected != -1:
            maxErrMsg = page.textDict['pbMaxSelectedErrorMsg']
            maxErrMsg %= page.maxNumSelected
        if page.minNumSelected != -1 and page.maxNumSelected != -1:
            minMaxErrMsg = page.textDict['pbMinMaxSelectedErrorMsg']
            minMaxErrMsg %= (page.minNumSelected, page.maxNumSelected)
    
    doMinMaxClickedCheck = ("verifySelectedWithinRange("
                            "%d,%d,'%s','%s','%s','%s')")
    doMinMaxClickedCheck %= (page.minNumSelected,
                             page.maxNumSelected,
                             page.pageName,
                             minErrMsg, maxErrMsg, minMaxErrMsg)

    return doMinMaxClickedCheck


def _getKeyPressEmbed(playID, submitID, doBoundariesAndProminences=False):
    
    bindKeyTxt = ""
    
    # Bind key press to play button?
    if playID is not None:
        clickJS = 'document.getElementById("%s").click();' % "button0"
        bindTuple = (playID, clickJS)
        bindKeyTxt += ("\n" + html.bindKeySubSnippetJS % bindTuple)
        
    # Bind key press to submit event?
    if submitID is not None:
        if doBoundariesAndProminences is True:
            js = "bpProcessKeyboardPress(e,%d)"
        else:
            js = html.bindToSubmitButtonJS
        bindKeyTxt += ("\n" + js % submitID)
    
    returnJS = ""
    if bindKeyTxt != "":
        returnJS = html.bindKeyJSTemplate % bindKeyTxt
    
    return returnJS


class BoundaryOrProminenceAbstractPage(abstract_pages.AbstractPage):
    
    def __init__(self, name, transcriptName, minPlays, maxPlays,
                 instructions, presentAudio="true", boundaryToken=None,
                 doProminence=True, syllableDemarcator=None,
                 bindPlayKeyID=None, bindSubmitID=None,
                 minNumSelected=-1, maxNumSelected=-1,
                 *args, **kargs):
        
        super(BoundaryOrProminenceAbstractPage, self).__init__(*args, **kargs)

        # Normalize variables
        if bindPlayKeyID is not None:
            bindPlayKeyID = html.keyboardletterToChar(bindPlayKeyID)
        if bindSubmitID is not None:
            bindSubmitID = html.keyboardletterToChar(bindSubmitID)
        presentAudio = presentAudio.lower() == "true"
        
        minNumSelected = int(minNumSelected)
        maxNumSelected = int(maxNumSelected)
        
        # Set instance variables
        self.name = name
        self.transcriptName = transcriptName
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        self.presentAudio = presentAudio
        self.boundaryToken = boundaryToken
        self.doProminence = doProminence
        self.syllableDemarcator = syllableDemarcator
        self.bindPlayKeyID = bindPlayKeyID
        self.bindSubmitID = bindSubmitID
        self.minNumSelected = minNumSelected
        self.maxNumSelected = maxNumSelected
        
        self.txtDir = self.webSurvey.txtDir
        self.wavDir = self.webSurvey.wavDir
        
        self.instructText = instructions
        
        # Strings used in this page
        txtKeyList = []
        txtKeyList.extend(abstract_pages.audioTextKeys)
        txtKeyList.append(self.instructText)
        
        if minNumSelected != -1:
            txtKeyList.append("pbMinSelectedErrorMsg")
        if maxNumSelected != -1:
            txtKeyList.append("pbMaxSelectedErrorMsg")
        if minNumSelected != -1 and maxNumSelected != -1:
            txtKeyList.append("pbMinMaxSelectedErrorMsg")
        
        self.textDict.update(self.batchGetText(txtKeyList))
        
        # Variables that all pages need to define
        if presentAudio is True:
            self.numAudioButtons = 1
        else:
            self.numAudioButtons = 0
        
        if self.doProminence is True:
            taskStr = "prominence"
        else:
            taskStr = "boundary"
        
        self.processSubmitList = ["audioLoader.verifyAudioPlayed()"]
        
        try:
            verifyNumSelected = _getTogglableWordEmbed(self)
        except TypeError:
            pass
        else:
            if verifyNumSelected is not None:
                self.processSubmitList.append(verifyNumSelected)
        
        prominenceStr = "true" if self.doProminence else "false"
        self.runOnLoad = "makeWordsVisibleCheckboxes(%s);\n" % prominenceStr
        
        self.checkArgs()
        
    def checkResponseCorrect(self, responseList, correctResponse):
        raise abstract_pages.NoCorrectResponseError()
    
    def checkArgs(self):
        
        # Make sure all audio files exist
        if self.presentAudio is True:
            audioFNList = [self.name + ext
                           for ext in self.webSurvey.audioExtList]
            if any([not os.path.exists(join(self.wavDir, fn))
                    for fn in audioFNList]):
                raise utils.FilesDoNotExist(self.wavDir, audioFNList, True)
        
        # Make sure all text files exist
        if not os.path.exists(join(self.txtDir, self.transcriptName + ".txt")):
            raise utils.FilesDoNotExist(self.txtDir,
                                        [self.transcriptName + ".txt", ],
                                        True)
        
    def getValidation(self):
        template = ""
        
        return template
        
    def getNumOutputs(self):
        # One binary label for every word
        
        transcriptFN = join(self.txtDir, self.transcriptName + ".txt")
        if self.syllableDemarcator is None:
            numOutputs = loader.getNumWords(transcriptFN)
        else:
            textList = loader.splitTranscript(transcriptFN)
            countList = [len(word.split(self.syllableDemarcator))
                         for row in textList
                         for word in row]
            numOutputs = sum(countList)
            
        return numOutputs
        
    def getOutput(self, form):
        
        try:
            retList = super(BoundaryOrProminenceAbstractPage,
                            self).getOutput(form)
        except abstract_pages.KeyNotInFormError:
            retList = ",".join(["0", ] * self.getNumOutputs())
            
        return retList
        
    def getHTML(self):
        '''
        Returns html for a page where users mark either breaks or prominence
        
        
        '''
        pageTemplate = join(constants.htmlDir, "wavTemplate.html")
        
        txtFN = join(self.txtDir, self.transcriptName + ".txt")
        
        sentenceList = loader.loadTxtFile(txtFN)
        
        testType = self.pageName
        
        # Construct the HTML here
        
        htmlTxt = _doBreaksOrProminence(testType, 0, 0,
                                        self.name,
                                        self.textDict[self.instructText],
                                        self.textDict['play_button'],
                                        sentenceList, self.presentAudio,
                                        self.boundaryToken,
                                        self.syllableDemarcator)[0]
    
        if self.presentAudio is True:
            embedTxt = ""
            embed = audio.generateEmbed(self.wavDir,
                                        [self.name, ],
                                        self.webSurvey.audioExtList,
                                        "audio")
            embedTxt += "\n\n" + embed
            embedTxt += _getKeyPressEmbed(self.bindPlayKeyID,
                                          self.bindSubmitID)
        else:
            embedTxt = ""
        embedTxt += "\n\n"
        
        htmlTxt = html.makeNoWrap(htmlTxt)
        
        return htmlTxt, pageTemplate, {'embed': embedTxt}


class BoundaryPage(BoundaryOrProminenceAbstractPage):
    
    pageName = "boundary"
    
    def __init__(self, *args, **kargs):
        kargs["doProminence"] = False
        super(BoundaryPage, self).__init__(*args, **kargs)
    
    
class ProminencePage(BoundaryOrProminenceAbstractPage):
    
    pageName = "prominence"
    
    def __init__(self, *args, **kargs):
        kargs["doProminence"] = True
        super(ProminencePage, self).__init__(*args, **kargs)


class SyllableMarking(BoundaryOrProminenceAbstractPage):
    
    pageName = "syllable_marking"
    
    def __init__(self, *args, **kargs):
        kargs["doProminence"] = True
        super(SyllableMarking, self).__init__(*args, **kargs)
   

class BoundaryAndProminencePage(abstract_pages.AbstractPage):

    pageName = 'boundary_and_prominence'

    def __init__(self, name, transcriptName, minPlays, maxPlays,
                 boundaryInstructions, prominenceInstructions,
                 presentAudio="true", boundaryToken=None,
                 bindPlayKeyID=None, bindSubmitID=None,
                 minNumSelected=-1, maxNumSelected=-1,
                 *args, **kargs):
        
        super(BoundaryAndProminencePage, self).__init__(*args, **kargs)
        
        # Sanity force
        if presentAudio.lower() == "false":
            minPlays = "0"
        
        # Normalize variables
        if bindPlayKeyID is not None:
            bindPlayKeyID = html.keyboardletterToChar(bindPlayKeyID)
        if bindSubmitID is not None:
            bindSubmitID = html.keyboardletterToChar(bindSubmitID)
        presentAudio = presentAudio.lower() == "true"
        
        minNumSelected = int(minNumSelected)
        maxNumSelected = int(maxNumSelected)
        
        # Set instance variables
        self.name = name
        self.transcriptName = transcriptName
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        self.presentAudio = presentAudio
        self.boundaryToken = boundaryToken
        self.bindPlayKeyID = bindPlayKeyID
        self.bindSubmitID = bindSubmitID
        self.minNumSelected = minNumSelected
        self.maxNumSelected = maxNumSelected
        
        self.txtDir = self.webSurvey.txtDir
        self.wavDir = self.webSurvey.wavDir
        
        self.stepOneInstructText = boundaryInstructions
        self.stepTwoInstructText = prominenceInstructions
        
        # Strings used in this page
        txtKeyList = ['continue_button']
        txtKeyList.extend(abstract_pages.audioTextKeys)
        txtKeyList.extend([self.stepOneInstructText,
                           self.stepTwoInstructText])
        
        if minNumSelected != -1:
            txtKeyList.append("pbMinSelectedErrorMsg")
        if maxNumSelected != -1:
            txtKeyList.append("pbMaxSelectedErrorMsg")
        if minNumSelected != -1 and maxNumSelected != -1:
            txtKeyList.append("pbMinMaxSelectedErrorMsg")
        
        self.textDict.update(self.batchGetText(txtKeyList))
        
        # Variables that all pages need to define
        if presentAudio is True:
            # Only show one at a time, plays the same audio
            self.numAudioButtons = 2
        else:
            self.numAudioButtons = 0
            
        self.processSubmitList = ["audioLoader.verifyAudioPlayed()", ]
        
        try:
            verifyNumSelected = _getTogglableWordEmbed(self)
        except TypeError:
            pass
        else:
            if verifyNumSelected is not None:
                self.processSubmitList.append(verifyNumSelected)
        
        self.runOnLoad = "makeWordsVisibleCheckboxes(false);\n"
    
    def checkResponseCorrect(self, responseList, correctResponse):
        raise abstract_pages.NoCorrectResponseError()
    
    def getValidation(self):
        template = ""
        
        return template
    
    def getNumOutputs(self):
        # 1 binary boundary mark and 1 prominence mark for every word
        numWords = loader.getNumWords(join(self.txtDir,
                                           self.transcriptName + ".txt"))
        return numWords * 2
    
    def getOutput(self, form):
        
        try:
            retList = super(BoundaryAndProminencePage, self).getOutput(form)
        except abstract_pages.KeyNotInFormError:
            retList = ",".join(["0", ] * self.getNumOutputs())
            
        return retList
    
    def getHTML(self):
        '''
        Returns html for a page where users mark both breaks and prominence
        
        Subjects first mark up the boundaries.  They are then shown the same
        utterance with their original markings still present.  They are then
        asked to mark boundaries.
        
        'focus' - either 'meaning' or 'acoustics' -- used to print the correct
            instructions
        '''
        
        pageTemplate = join(constants.htmlDir, "wavTemplate.html")
        
        txtFN = join(self.txtDir, self.transcriptName + ".txt")
        
        sentenceList = loader.loadTxtFile(txtFN)
        
        # Construct the HTML here
        # There are two passes of the utterance.  The first is for boundaries.
        # After
        wordIDNum = 0
        htmlTxt = '<div id="ShownDiv" style="DISPLAY: block">'
    
        # HTML boundaries
        audioLabel = self.textDict['play_button']
        stepOneInstructText = self.textDict[self.stepOneInstructText]
        tmpHTMLTxt, numWords = _doBreaksOrProminence(self.pageName,
                                                     wordIDNum, 0,
                                                     self.name,
                                                     stepOneInstructText,
                                                     audioLabel,
                                                     sentenceList,
                                                     self.presentAudio,
                                                     self.boundaryToken,
                                                     None)
        htmlTxt += "<div>%s</div>" % tmpHTMLTxt
    
        # HTML from transitioning from the boundary portion of text
        # to the prominence portion
        continueButtonTxt = self.textDict['continue_button']
        htmlTxt += '''<br /><br /><input type="button" value="%s"
                    id="halfwaySubmitButton"
                    onclick="ShowHide(audioLoader.verifyFirstAudioPlayed(), %s)"></button>''' % (continueButtonTxt, _getTogglableWordEmbed(self))
        htmlTxt += '</div>\n\n<div id="HiddenDiv" style="DISPLAY: none">\n\n'
        
        # HTML prominence
        stepTwoInstructText = self.textDict[self.stepTwoInstructText]
        htmlTxt += _doBreaksOrProminence(self.pageName, numWords, 1,
                                         self.name,
                                         stepTwoInstructText,
                                         audioLabel,
                                         sentenceList,
                                         self.presentAudio,
                                         self.boundaryToken,
                                         None)[0]
        htmlTxt += "</div>"
                    
        # Add the javascript and style sheets here
        if self.presentAudio is True:
            embedTxt = ""
            embed = audio.generateEmbed(self.wavDir,
                                        [self.name, ],
                                        self.webSurvey.audioExtList,
                                        "audio")
            embedTxt += "\n\n" + embed
            embedTxt += "\n\n" + _getKeyPressEmbed(self.bindPlayKeyID,
                                                   self.bindSubmitID,
                                                   True)
                
        else:
            embedTxt = ""
        
        htmlTxt = html.makeNoWrap(htmlTxt)
        
        return htmlTxt, pageTemplate, {'embed': embedTxt}
