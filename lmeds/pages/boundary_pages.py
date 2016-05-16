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
from lmeds.io import loader
from lmeds.pages import abstract_pages


def _doBreaksOrProminence(testType, wordIDNum, audioNum, name, textNameStr,
                          sentenceList, presentAudioFlag, token,
                          syllableDemarcator):
    '''
    This is a helper function.  It does not construct a full page.
    
    Can be used to prepare text for prominence OR boundary annotation
    (or both if called twice and aggregated).
    '''
    
    htmlTxt = ""
    
    instrMsg = ("%s<br /><br />\n\n" % textNameStr)
    htmlTxt += html.makeWrap(instrMsg)
    
    if presentAudioFlag.lower() == 'true':
        htmlTxt += audio.generateAudioButton(name, audioNum, False)
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
                    tmpHTMLTxt += "\n"

            sentenceListTxtList.append(tmpHTMLTxt)
    
    newTxt = "<br /><br />\n\n".join(sentenceListTxtList)
            
    htmlTxt += newTxt
            
    return htmlTxt, wordIDNum


def _getProminenceOrBoundaryWordEmbed(isProminence):
    
    boundaryEmbed = """
    $(this).closest("label").css({
        borderRight: this.checked ? "3px solid #000000":"0px solid #FFFFFF"
    });
    $(this).closest("label").css({ paddingRight: this.checked ? "0px":"3px"});
    """
    
    prominenceEmbed = """
    $(this).closest("label").css({ color: this.checked ? "red":"black"});
    """
    
    javascript = """
<script type="text/javascript" src="//code.jquery.com/jquery-1.11.0.min.js">
</script>
<script>if (!window.jQuery) { document.write(
'<script src="../html/jquery-1.11.0.min.js"><\/script>'); }
</script>
    
<style type="text/css">
           /* Style the label so it looks like a button */
           .rptWordPadding {
                padding-right: 3px;
                padding-left: 3px;
           }
           label.syllable {
                border-right: 0px solid #FFFFFF;
                position: relative;
                z-index: 3;
                padding-right: 0px;
                padding-left: 0px;
           }
           label.word {
                border-right: 0px solid #FFFFFF;
                position: relative;
                z-index: 3;
                padding-right: 3px;
                padding-left: 3px;
           }
           /* CSS to make the checkbox disappear (but remain functional) */
           label input {
                position: absolute;
                visibility: hidden;
           }
</style>
    
    
<script>
$(document).ready(function(){
  $('input[type=checkbox]').click(function(){
%s
  });
});
</script>
"""
    
    if isProminence:
        javascript %= prominenceEmbed
    else:
        javascript %= boundaryEmbed

    return javascript


def _makeTogglableWord(testType, word, idNum, boundaryToken, labelClass):
    
    tokenTxt = ""
    if boundaryToken is not None:
        tokenTxt = """<span class="hidden">%s</span>""" % boundaryToken
    
    htmlTxt = ('<label for="%(idNum)d" class="%(class)s">'
               '<input type="checkbox" name="%(testType)s" id="%(idNum)d"'
               'value="%(idNum)d"/>'
               '%(word)s' + tokenTxt + '</label>')

    return htmlTxt % {"testType": testType, "word": word, "idNum": idNum,
                      "class": labelClass}


def _getTogglableWordEmbed(numWords, boundaryMarking):
    
    boundaryMarkingCode_showHide = """
        $("#"+x).closest("label").css({
        borderRight: "3px solid #000000"
        });
        $("#"+x).closest("label").css({ paddingRight: "0px"});
        """
    
    boundaryMarkingCode_toggle = """
        $(this).closest("label").css({
        borderRight: this.checked ? "3px solid #000000":"0px solid #FFFFFF"
        });
        $(this).closest("label").css({
        paddingRight: this.checked ? "0px":"3px"
        });"""
    
    if boundaryMarking is not None:
        boundaryMarkingCode_toggle = """
            $(this).next("span").css({
                visibility: this.checked ? "visible":"hidden"
            });"""
        boundaryMarkingCode_showHide = """
            $("#"+x).next("span").css({ visibility: "visible"});
            """
    
    javascript = """
<script type="text/javascript" src="//code.jquery.com/jquery-1.11.0.min.js">
</script>
<script>if (!window.jQuery) { document.write(
'<script src="../html/jquery-1.11.0.min.js"><\/script>'); }
</script>

<script>
function ShowHide()
{
var didPlay = verifyFirstAudioPlayed();

if(didPlay == true) {
    document.getElementById("ShownDiv").style.display='none';
    document.getElementById("HiddenDiv").style.display='block';
    document.getElementById("HiddenForm").style.display='block';
    for (e=0;e<%(numWords)d;e++) {
        var x = e+%(numWords)d;

        if (document.getElementById(e).checked==true) {
%(boundaryMarkingCode_showHide)s
            }
        }
    }

    $('html, body').animate({ scrollTop: 0 }, 'fast');
}
</script>
    
<style type="text/css">
           /* Style the label so it looks like a button */
           rptWordPadding {
                padding-right: 3px;
                padding-left: 3px;
           }
           label.syllable {
                border-right: 0px solid #FFFFFF;
                position: relative;
                z-index: 3;
                padding-right: 0px;
                padding-left: 0px;
           }
           label.word {
                border-right: 0px solid #FFFFFF;
                position: relative;
                z-index: 3;
                padding-right: 3px;
                padding-left: 3px;
           }
           /* CSS to make the checkbox disappear (but remain functional) */
           label input {
                position: absolute;
                visibility: hidden;
           }
</style>
    
    
<script>
$(document).ready(function(){
  $('input[type=checkbox]').click(function(){
    
    if (this.value < %(numWords)d)
    {
    /* Boundary marking */
%(boundaryMarkingCode_toggle)s
    }
    else
    {
    /* Prominence marking */
    $(this).closest("label").css({ color: this.checked ? "red":"black"});
    }
  });
});
</script>"""

    return javascript % {"numWords":
                         numWords,
                         "boundaryMarkingCode_toggle":
                         boundaryMarkingCode_toggle,
                         "boundaryMarkingCode_showHide":
                         boundaryMarkingCode_showHide}


class BoundaryOrProminenceAbstractPage(abstract_pages.AbstractPage):
    
    def __init__(self, name, transcriptName, minPlays, maxPlays,
                 instructions, presentAudio="true", boundaryToken=None,
                 doProminence=True, syllableDemarcator=None,
                 *args, **kargs):
        
        super(BoundaryOrProminenceAbstractPage, self).__init__(*args, **kargs)
        
        self.name = name
        self.transcriptName = transcriptName
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        self.presentAudio = presentAudio
        self.boundaryToken = boundaryToken
        self.doProminence = doProminence
        self.syllableDemarcator = syllableDemarcator
        
        self.txtDir = self.webSurvey.txtDir
        self.wavDir = self.webSurvey.wavDir
        
        self.instructText = instructions
    
        # Strings used in this page
        txtKeyList = []
        txtKeyList.extend(abstract_pages.audioTextKeys)
        txtKeyList.append(self.instructText)
        self.textDict.update(loader.batchGetText(txtKeyList))
    
        # Variables that all pages need to define
        if presentAudio == "true":
            self.numAudioButtons = 1
        else:
            self.numAudioButtons = 0
        self.processSubmitList = ["verifyAudioPlayed", ]
        
        self.checkArgs()
        
    def checkResponseCorrect(self, responseList, correctResponse):
        raise abstract_pages.NoCorrectResponseError()
    
    def checkArgs(self):
        
        # Make sure all audio files exist
        audioFNList = [self.name + ext for ext in self.webSurvey.audioExtList]
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
                                        sentenceList, self.presentAudio,
                                        self.boundaryToken,
                                        self.syllableDemarcator)[0]
    
        if self.presentAudio:
            embedTxt = audio.getPlaybackJS(True, 1, self.maxPlays,
                                           self.minPlays)
            embed = audio.generateEmbed(self.wavDir,
                                        [self.name, ],
                                        self.webSurvey.audioExtList,
                                        "audio")
            embedTxt += "\n\n" + embed
        else:
            embedTxt = ""
        embedTxt += "\n\n"
        embedTxt += _getProminenceOrBoundaryWordEmbed(self.doProminence)
        
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
                 presentAudio="true", boundaryToken=None, *args, **kargs):
        
        super(BoundaryAndProminencePage, self).__init__(*args, **kargs)
        
        # Sanity force
        if presentAudio.lower() == "false":
            minPlays = "0"
        
        self.name = name
        self.transcriptName = transcriptName
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        self.presentAudio = presentAudio
        self.boundaryToken = boundaryToken
        
        self.txtDir = self.webSurvey.txtDir
        self.wavDir = self.webSurvey.wavDir
        
        self.stepOneInstructText = boundaryInstructions
        self.stepTwoInstructText = prominenceInstructions
        
        # Strings used in this page
        txtKeyList = ['continue_button']
        txtKeyList.extend(abstract_pages.audioTextKeys)
        txtKeyList.extend([self.stepOneInstructText,
                           self.stepTwoInstructText])
        self.textDict.update(loader.batchGetText(txtKeyList))
        
        # Variables that all pages need to define
        if presentAudio == "true":
            # Only show one at a time, plays the same audio
            self.numAudioButtons = 2
        else:
            self.numAudioButtons = 0
        self.processSubmitList = ["verifyAudioPlayed", ]
    
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
        stepOneInstructText = self.textDict[self.stepOneInstructText]
        tmpHTMLTxt, numWords = _doBreaksOrProminence(self.pageName,
                                                     wordIDNum, 0,
                                                     self.name,
                                                     stepOneInstructText,
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
                    onclick="ShowHide()"></button>''' % continueButtonTxt
        htmlTxt += '</div>\n\n<div id="HiddenDiv" style="DISPLAY: none">\n\n'
        
        # HTML prominence
        stepTwoInstructText = self.textDict[self.stepTwoInstructText]
        htmlTxt += _doBreaksOrProminence(self.pageName, numWords, 1,
                                         self.name,
                                         stepTwoInstructText,
                                         sentenceList,
                                         self.presentAudio,
                                         self.boundaryToken,
                                         None)[0]
        htmlTxt += "</div>"
                    
        # Add the javascript and style sheets here
        if self.presentAudio:
            embedTxt = audio.getPlaybackJS(True, 2, self.maxPlays,
                                           self.minPlays)
            embed = audio.generateEmbed(self.wavDir,
                                        [self.name, ],
                                        self.webSurvey.audioExtList,
                                        "audio")
            embedTxt += "\n\n" + embed
        else:
            embedTxt = ""

        embedTxt += "\n\n" + _getTogglableWordEmbed(numWords,
                                                    self.boundaryToken)
        
        htmlTxt = html.makeNoWrap(htmlTxt)
        
        return htmlTxt, pageTemplate, {'embed': embedTxt}
