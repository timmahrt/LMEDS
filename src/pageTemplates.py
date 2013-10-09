'''
Created on May 30, 2013

@author: timmahrt
'''

from os.path import join

from functools import partial

import audio
import html
import loader
import constants


def finalPage():
    htmlText = loader.getText('test complete')
    pageTemplate = join(constants.htmlDir, "finalPageTemplate.html")

    return htmlText, pageTemplate, {}


def checkForAudioTag():
    txt = '''
    <script>
    
function isSupportedBrowser() {

if(!!document.createElement('audio').canPlayType == false) {
    document.getElementById("submit").disabled = true;
    document.getElementById("unsupported_warning").style.display='block';
}

    }
    window.onload = isSupportedBrowser;
    </script>
    '''

    return txt


def loginPage():
    htmlText = html.firstPageHTML()
    pageTemplate = join(constants.htmlDir, "blankPageWValidation.html")

    embedTxt = checkForAudioTag()

    return htmlText, pageTemplate, {'embed':embedTxt}


def loginBadUserPage(userName):
    htmlText = html.firstPageErrorHTML() % userName
    pageTemplate = join(constants.htmlDir, "blankPageWValidation.html")
    
    return htmlText, pageTemplate, {}


def consentPage():
    htmlText = html.consentPageHTML()
    pageTemplate = join(constants.htmlDir, "blankPageWValidation.html")

    return htmlText, pageTemplate, {}


def consentEndPage():
    htmlText = loader.getText('consent opt out')
    pageTemplate = join(constants.htmlDir, "finalPageTemplate.html")

    return htmlText, pageTemplate, {}


def instructionPage(instructionsName):
    
    name = "%s instructions" % instructionsName
    
    htmlText = '''<p id="title">
%s
</p><br /><br />

<u><b> Section </b></u> 
<br /><br />

<div id="longText">

%s

</div><br />''' % (loader.getText('title'), loader.getText(name))
    
    
#     htmlText = open(join(constants.instructDir, instructionsName+".html"), "r").read()
    
    
    
#    htmlText = html.instructionPageHTML()
    pageTemplate = join(constants.htmlDir, "basicTemplate.html")
    
    return htmlText, pageTemplate, {}
    
    
def breakPage():
    htmlText = html.breakPageHTML()
    pageTemplate = join(constants.htmlDir, "basicTemplate.html")
    
    return htmlText, pageTemplate, {}


def textAnnotationPage(name, doBreaks, doProminence, txtDir, wavDir):
    pageTemplate = join(constants.htmlDir, "wavTemplate.html")
    
    txtFN = join(txtDir, name+".txt")
    
    sentenceList = loader.loadTxt(txtFN)
        
    
    htmlText = audio.generateAudioButton(name, 0, False) + "<br />"
    
    offsetNum = 0
    for sentence in sentenceList:
        wordList = sentence.split(" ")
        htmlText += html.constructTable(wordList, doBreaks, doProminence, offsetNum)
        offsetNum += len(wordList)
        
    embedTxt = audio.getPlayAudioJavaScript(True, 1, [2,])
    embedTxt += "\n\n" + audio.generateEmbed(wavDir, [name,])

    htmlText = _makeNoWrap(htmlText)

    return htmlText, pageTemplate, {'embed':embedTxt}


def _doBreaksOrProminence(testType, wordIDNum, audioNum, name, textName, sentenceList):
    '''
    This is a helper function.  It does not construct a full page.
    
    Can be used to prepare text for prominence OR boundary annotation
    (or both if called twice and aggregated).
    '''
    
    htmlTxt = ""
    
    instrMsg = ("%s<br /><br />\n\n" % loader.getText(textName))
    htmlTxt += _makeWrap(instrMsg)
    
    htmlTxt += audio.generateAudioButton(name, audioNum, False) + "<br /><br />\n\n"
    for sentence in sentenceList:
        wordList = sentence.split(" ")
        for word in wordList:
            htmlTxt += html.makeTogglableWord(testType, word, wordIDNum)
            wordIDNum += 1 
        
        # New sentence, new line
        htmlTxt += "<br /><br />\n\n"
            
    return htmlTxt, wordIDNum


def breaksOrProminencePage(name, doProminence, txtDir, wavDir):
    '''
    Returns html for a page where users mark either breaks or prominence
    
    
    '''
    pageTemplate = join(constants.htmlDir, "wavTemplate.html")
    
    txtFN = join(txtDir, name+".txt")
    
    sentenceList = loader.loadTxt(txtFN)
    
    if doProminence:
        textName = "prominence instructions short"
        testType = "p"
    else:
        textName = "boundary instructions short"
        testType = "b"
    
    # Construct the HTML here
    htmlTxt = _doBreaksOrProminence(testType, 0, 0, name, textName, sentenceList)[0]

    embedTxt = audio.getPlayAudioJavaScript(True, 1, [2,])
    embedTxt += "\n\n" + audio.generateEmbed(wavDir, [name,])
    embedTxt += "\n\n" + html.getProminenceOrBoundaryWordEmbed(doProminence)
    
    htmlTxt = _makeNoWrap(htmlTxt)
    
    return htmlTxt, pageTemplate, {'embed':embedTxt}
    
    
def breaksAndProminencePage(name, focus, txtDir, wavDir):
    '''
    Returns html for a page where users mark both breaks and prominence
    
    Subjects first mark up the boundaries.  They are then shown the same utterance
    with their original markings still present.  They are then asked to mark
    boundaries.
    
    'focus' - either 'meaning' or 'acoustics' -- used to print the correct
        instructions
    '''
    
    pageTemplate = join(constants.htmlDir, "wavTemplate.html")
    
    txtFN = join(txtDir, name+".txt")
    
    sentenceList = loader.loadTxt(txtFN)
    
    # Construct the HTML here
    # There are two passes of the utterance.  The first is for boundaries.
    # After
    wordIDNum = 0
    numWords = 0
    htmlTxt = '<div id="ShownDiv" style="DISPLAY: block">'

    # HTML boundaries
    tmpHTMLTxt, numWords = _doBreaksOrProminence("b_and_p", wordIDNum, 0, name, 
                                                 "boundary_%s instructions short" % focus, 
                                                 sentenceList)
    htmlTxt += tmpHTMLTxt

    # HTML from transitioning from the boundary portion of text to the prominence portion
    htmlTxt += '<br /><br /><input type="button" value="Submit" onclick="ShowHide()"></button>'
    htmlTxt += '</div>\n\n<div id="HiddenDiv" style="DISPLAY: none">\n\n'
    
    # HTML prominence
    htmlTxt += _doBreaksOrProminence("b_and_p", numWords, 1, name, 
                                     "prominence_%s post boundary instructions short" % focus, 
                                     sentenceList)[0]
    htmlTxt += "</div>"
                
    # Closing off the div for the prominence section
    #htmlTxt += '</div>' # The last div will be closed off by 'formTemplate2'
                
    # Add the javascript and style sheets here
    embedTxt = audio.getPlayAudioJavaScript(True, 2, [2,2,])
    embedTxt += "\n\n" + audio.generateEmbed(wavDir, [name,])
    embedTxt += "\n\n" + html.getTogglableWordEmbed(numWords)
    
    htmlTxt = _makeNoWrap(htmlTxt)
    
    return htmlTxt, pageTemplate, {'embed':embedTxt}
    
    
def axbPage(sourceNameX, compareNameA, compareNameB, wavDir):
    pageTemplate = join(constants.htmlDir, "axbTemplate.html")
    
    xHTML = audio.generateAudioButton(sourceNameX, 0, False)
    aHTML = audio.generateAudioButton(compareNameA, 1, False)
    bHTML = audio.generateAudioButton(compareNameB, 2, False)
    
    htmlText = html.axbPageHTML()
    htmlText %= (xHTML, aHTML, bHTML)
    
    embedTxt = audio.getPlayAudioJavaScript(True, 3, [2,2,2,])
    embedTxt += "\n\n" + audio.generateEmbed(wavDir, [sourceNameX, compareNameA, compareNameB])
    
    htmlText = _makeNoWrap(htmlText)
    
    return htmlText, pageTemplate, {'embed':embedTxt}


def audioDecisionPage(audioName, wavDir):
    '''
    Listeners hear one file and decide if its an example of "textA", "textB" or "None"
    '''
    pageTemplate = join(constants.htmlDir, "axbTemplate.html")
    
    aHTML = audio.generateAudioButton(audioName, 0, False)
    
    description = loader.getText("abn text")
    
    htmlText = description + html.audioDecisionPageHTML()
    htmlText %= (aHTML, "Broad Focus", "Contrastive Focus", "Neither")
    
    embedTxt = audio.getPlayAudioJavaScript(True, 1, [1,])
    embedTxt += "\n\n" + audio.generateEmbed(wavDir, [audioName])

    return htmlText, pageTemplate, {'embed':embedTxt}


def _makeNoWrap(htmlTxt):
    return '<div id="noTextWrapArea">\n\n%s\n\n</div>' % htmlTxt


def _makeWrap(htmlTxt):
    return '<div id="textWrapArea">\n\n%s\n\n</div>' % htmlTxt


def getPageTemplates(webSurvey):
    
    testKeyDict = {'login':loginPage, 'login_bad_user_name':loginBadUserPage,
                   'consent':consentPage, 'consent_end':consentEndPage,
                   'instruct':instructionPage,
                   'break':breakPage,
                    'end':finalPage,
                    'prominence':partial(breaksOrProminencePage, txtDir=webSurvey.txtDir,
                                         wavDir=webSurvey.wavDir, doProminence=True),
                    'boundary':partial(breaksOrProminencePage, txtDir=webSurvey.txtDir,
                                         wavDir=webSurvey.wavDir, doProminence=False),
                    'boundaryAndProminence':partial(breaksAndProminencePage, txtDir=webSurvey.txtDir,
                                         wavDir=webSurvey.wavDir),
                    'prominenceOld':partial(textAnnotationPage, txtDir=webSurvey.txtDir, 
                                         wavDir=webSurvey.wavDir, doBreaks=False, doProminence=True), 
                    'boundaryOld':partial(textAnnotationPage, txtDir=webSurvey.txtDir, 
                                         wavDir=webSurvey.wavDir, doBreaks=True, doProminence=False),
                    'axb':partial(axbPage, wavDir=webSurvey.wavDir),
                    'abn':partial(audioDecisionPage, wavDir=webSurvey.wavDir)}
    
#    knownKeyList = testKeyDict.keys()
    
    return testKeyDict

