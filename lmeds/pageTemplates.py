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
    <script type="text/javascript">
    
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


def audioTestPage(name, wavDir):
    
    htmlText = html.audioTestPageHTML()
    pageTemplate = join(constants.htmlDir, "blankPageWValidation.html")
    
    htmlText %= audio.generateAudioButton(name, 0, False) + "<br />"
    
    embedTxt = audio.getPlayAudioJavaScript(True, 1, [-1,], 1)
    embedTxt += "\n\n" + audio.generateEmbed(wavDir, [name,])
    
    return htmlText, pageTemplate, {'embed':embedTxt}


def audioTestEndPage():
    htmlText = loader.getText('audioTest no audio')
    pageTemplate = join(constants.htmlDir, "finalPageTemplate.html")
    
    return htmlText, pageTemplate, {}


def consentPage(consentName=None):
    htmlText = html.consentPageHTML(consentName)
    pageTemplate = join(constants.htmlDir, "blankPageWValidation.html")

    return htmlText, pageTemplate, {}


def consentEndPage():
    htmlText = loader.getText('consent opt out')
    pageTemplate = join(constants.htmlDir, "finalPageTemplate.html")

    return htmlText, pageTemplate, {}


def instructionPage(*name):
    
    name = " ".join(name)
    
    htmlText = '''<p id="title">
%s
</p><br /><br />

<div id="longText">

%s

</div><br />''' % (loader.getText('title'), loader.getText(name))
    
    
#     htmlText = open(join(constants.instructDir, instructionsName+".html"), "r").read()
#    htmlText = html.instructionPageHTML()
    pageTemplate = join(constants.htmlDir, "basicTemplate.html")
    
    return htmlText, pageTemplate, {}
    
    
def audioInstructionPage(instrName, *audioNameList, **kargs):

    audioNameList = [name.strip() for name in audioNameList]
    audioButtonList = [audio.generateAudioButton(name, i, False) for i, name in enumerate(audioNameList)]
    
    tmpTxt = loader.getText(instrName) % tuple(audioButtonList)
    htmlText = '''<p id="title">
%s
</p><br /><br />

<div id="longText">

%s

</div><br />''' % (loader.getText('title'), tmpTxt)
    
    
    embedTxt = audio.getPlayAudioJavaScript(True, len(audioNameList), [-1,]*len(audioNameList), 1)
    embedTxt += "\n\n" + audio.generateEmbed(kargs['wavDir'], audioNameList)
    
    pageTemplate = join(constants.htmlDir, "basicTemplate.html")
    
    return htmlText, pageTemplate, {'embed':embedTxt}
    
    
def surveyPage(surveyFN, surveyPath):
    htmlText, embedTxt = html.surveyPage(join(surveyPath, surveyFN + ".txt"))
    pageTemplate = join(constants.htmlDir, "basicTemplate.html")
    
    return htmlText, pageTemplate, {'embed':embedTxt}
    
    
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
        htmlText += html.constructCheckboxTable(wordList, doBreaks, doProminence, offsetNum)
        offsetNum += len(wordList)
        
    embedTxt = audio.getPlayAudioJavaScript(True, 1, [2,], 1)
    embedTxt += "\n\n" + audio.generateEmbed(wavDir, [name,])

    htmlText = _makeNoWrap(htmlText)

    return htmlText, pageTemplate, {'embed':embedTxt}


def _doBreaksOrProminence(testType, wordIDNum, audioNum, name, textName, sentenceList, presentAudioFlag, token):
    '''
    This is a helper function.  It does not construct a full page.
    
    Can be used to prepare text for prominence OR boundary annotation
    (or both if called twice and aggregated).
    '''
    
    htmlTxt = ""
    
    instrMsg = ("%s<br /><br />\n\n" % loader.getText(textName))
    htmlTxt += _makeWrap(instrMsg)
    
    if presentAudioFlag.lower() == 'true':
        htmlTxt += audio.generateAudioButton(name, audioNum, False) + "<br /><br />\n\n"
    else:
        htmlTxt += "<br /><br />\n\n"
    
    sentenceListTxtList = []
    for sentence in sentenceList:
        wordList = sentence.split(" ")
        tmpHTMLTxt = ""
        for word in wordList:
            tmpHTMLTxt += html.makeTogglableWord(testType, word, wordIDNum, token)
            wordIDNum += 1 
        
        # New sentence, new line
        sentenceListTxtList.append(tmpHTMLTxt)
    
    newTxt = "<br /><br />\n\n".join(sentenceListTxtList)
#     htmlTxt += "<br /><br />\n\n"
            
    htmlTxt += newTxt
            
    return htmlTxt, wordIDNum


def breaksOrProminencePage(name, minPlays, maxPlays, instructions=None, presentAudio="true", boundaryToken=None, doProminence=True, txtDir=None, wavDir=None):
    '''
    Returns html for a page where users mark either breaks or prominence
    
    
    '''
    pageTemplate = join(constants.htmlDir, "wavTemplate.html")
    
    txtFN = join(txtDir, name+".txt")
    
    sentenceList = loader.loadTxt(txtFN)
    
    if doProminence:
        textName = ["prominence", "instructions short"]
        testType = "p"
    else:
        textName = ["boundary", "instructions short"]
        testType = "b"
    
    if instructions != None:
        textName.insert(1, instructions)
    
    # Construct the HTML here
    htmlTxt = _doBreaksOrProminence(testType, 0, 0, name, " ".join(textName), sentenceList, presentAudio, boundaryToken)[0]

    embedTxt = audio.getPlayAudioJavaScript(True, 1, [maxPlays,], minPlays)
    embedTxt += "\n\n" + audio.generateEmbed(wavDir, [name,])
    embedTxt += "\n\n" + html.getProminenceOrBoundaryWordEmbed(doProminence)
    
    htmlTxt = _makeNoWrap(htmlTxt)
    
    return htmlTxt, pageTemplate, {'embed':embedTxt}
    
    
def breaksAndProminencePage(name, minPlays, maxPlays, instructions=None, presentAudio="true", boundaryToken=None, txtDir=None, wavDir=None):
    '''
    Returns html for a page where users mark both breaks and prominence
    
    Subjects first mark up the boundaries.  They are then shown the same utterance
    with their original markings still present.  They are then asked to mark
    boundaries.
    
    'focus' - either 'meaning' or 'acoustics' -- used to print the correct
        instructions
    '''
    
    # Sanity force
    if presentAudio.lower() == "false":
        minPlays = "0"
    
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
    instructionsText = ["boundary", "instructions short"]
    if instructions != None:
        instructionsText.insert(1, instructions)
    tmpHTMLTxt, numWords = _doBreaksOrProminence("b_and_p", wordIDNum, 0, name, 
                                                 " ".join(instructionsText), 
                                                 sentenceList,
                                                 presentAudio, 
                                                 boundaryToken)
    htmlTxt += "<div>%s</div>" % tmpHTMLTxt

    # HTML from transitioning from the boundary portion of text to the prominence portion
    htmlTxt += '<br /><br /><input type="button" value="%s" onclick="ShowHide()"></button>' % loader.getText('continue button')
    htmlTxt += '</div>\n\n<div id="HiddenDiv" style="DISPLAY: none">\n\n'
    
    # HTML prominence
    instructionsText = ["prominence", "post boundary instructions short"]
    if instructions != None:
        instructionsText.insert(1, instructions)
    htmlTxt += _doBreaksOrProminence("b_and_p", numWords, 1, name, 
                                     " ".join(instructionsText), 
                                     sentenceList,
                                     presentAudio,
                                     boundaryToken)[0]
    htmlTxt += "</div>"
                
    # Closing off the div for the prominence section
    #htmlTxt += '</div>' # The last div will be closed off by 'formTemplate2'
                
    # Add the javascript and style sheets here
    embedTxt = audio.getPlayAudioJavaScript(True, 2, [maxPlays,maxPlays,], minPlays)
    embedTxt += "\n\n" + audio.generateEmbed(wavDir, [name,])
    embedTxt += "\n\n" + html.getTogglableWordEmbed(numWords, boundaryToken)
    
    htmlTxt = _makeNoWrap(htmlTxt)
    
    return htmlTxt, pageTemplate, {'embed':embedTxt}
    
    
def axbPage(sourceNameX, compareNameA, compareNameB, minPlays, maxPlays, wavDir):
    pageTemplate = join(constants.htmlDir, "axbTemplate.html")
    
    xHTML = audio.generateAudioButton(sourceNameX, 0, False)
    aHTML = audio.generateAudioButton(compareNameA, 1, False)
    bHTML = audio.generateAudioButton(compareNameB, 2, False)
    
    htmlText = html.axbPageHTML()
    htmlText %= (xHTML, aHTML, bHTML)
    
    embedTxt = audio.getPlayAudioJavaScript(True, 3, [maxPlays,maxPlays,maxPlays,], minPlays)
    embedTxt += "\n\n" + audio.generateEmbed(wavDir, [sourceNameX, compareNameA, compareNameB])
    
    htmlText = _makeNoWrap(htmlText)
    
    return htmlText, pageTemplate, {'embed':embedTxt}


def audioDecisionPage(audioName, minPlays, maxPlays, wavDir):
    '''
    Listeners hear one file and decide if its an example of "textA", "textB" or "None"
    '''
    pageTemplate = join(constants.htmlDir, "axbTemplate.html")
    
    aHTML = audio.generateAudioButton(audioName, 0, False)
    
    description = loader.getText("abn text")
    
    a = loader.getText("abn a")
    b = loader.getText("abn b")
    n = loader.getText("abn n")
    
    htmlText = description + "<br />" + html.audioDecisionPageHTML()
    htmlText %= (aHTML, a, b, n)
    
    embedTxt = audio.getPlayAudioJavaScript(True, 1, [maxPlays,], minPlays)
    embedTxt += "\n\n" + audio.generateEmbed(wavDir, [audioName])

    return htmlText, pageTemplate, {'embed':embedTxt}


def sameDifferentPage(audioName1, audioName2, minPlays, maxPlays, wavDir):
    '''
    Listeners hear two files and decide if they are the same or different
    '''
    pageTemplate = join(constants.htmlDir, "axbTemplate.html")
    
    aHTML = audio.generateAudioButton(audioName1, 0, False)
    bHTML = audio.generateAudioButton(audioName2, 1, False)
    
    description = loader.getText("same_different text")
    
    sameTxt = loader.getText("same_different same")
    differentTxt = loader.getText("same_different different")
    
    htmlText = description + html.sameDifferentPageHTML()
    htmlText %= (aHTML, bHTML, sameTxt, differentTxt)

    embedTxt = audio.getPlayAudioJavaScript(True, 2, [maxPlays, maxPlays], minPlays)
    embedTxt += "\n\n" + audio.generateEmbed(wavDir, [audioName1, audioName2])

    return htmlText, pageTemplate, {'embed': embedTxt}


def _makeNoWrap(htmlTxt):
    return '<div id="noTextWrapArea">\n\n%s\n\n</div>' % htmlTxt


def _makeWrap(htmlTxt):
    return '<div id="textWrapArea">\n\n%s\n\n</div>' % htmlTxt


def getPageTemplates(webSurvey):
    
    testKeyDict = {'login':loginPage, 'login_bad_user_name':loginBadUserPage,
                   'consent':consentPage, 'consent_end':consentEndPage,
                   'survey':partial(surveyPage, surveyPath=webSurvey.surveyRoot),
                   'audio_test':partial(audioTestPage, wavDir=webSurvey.wavDir),
                   'audio_test_end':audioTestEndPage,
                   'text_page':instructionPage,
                   'text_and_audio_page':partial(audioInstructionPage, wavDir=webSurvey.wavDir),
                   'break':breakPage,
                    'end':finalPage,
                    'prominence':partial(breaksOrProminencePage, txtDir=webSurvey.txtDir,
                                         wavDir=webSurvey.wavDir, doProminence=True),
                    'boundary':partial(breaksOrProminencePage, txtDir=webSurvey.txtDir,
                                         wavDir=webSurvey.wavDir, doProminence=False),
                    'boundary_and_prominence':partial(breaksAndProminencePage, txtDir=webSurvey.txtDir,
                                         wavDir=webSurvey.wavDir),
                    'prominenceOld':partial(textAnnotationPage, txtDir=webSurvey.txtDir, 
                                         wavDir=webSurvey.wavDir, doBreaks=False, doProminence=True), 
                    'boundaryOld':partial(textAnnotationPage, txtDir=webSurvey.txtDir, 
                                         wavDir=webSurvey.wavDir, doBreaks=True, doProminence=False),
                    'axb':partial(axbPage, wavDir=webSurvey.wavDir),
                    'abn':partial(audioDecisionPage, wavDir=webSurvey.wavDir),
                    'same_different':partial(sameDifferentPage, wavDir=webSurvey.wavDir)}
    
#    knownKeyList = testKeyDict.keys()
    
    return testKeyDict


if __name__ == "__main__":
    pass

