'''
Created on Mar 1, 2014

@author: tmahrt

Core pages may appear in any LMEDS tests, regardless of what kind of
experiment it is.  Pages that provide information to users, get their
 user name or consent, error pages, etc.
'''

from os.path import join
import io

from lmeds.pages import abstract_pages
from lmeds.lmeds_io import loader
from lmeds.utilities import constants
from lmeds.code_generation import html
from lmeds.code_generation import audio

checkboxValidation = """
var y=document.forms["languageSurvey"];
if (checkBoxValidate(y["radio"])==true)
    {
    alert("%s");
    return false;
    }
return true;
"""


class LoginPage(abstract_pages.NonRecordingPage):
    
    pageName = "login"
    
    def __init__(self, *args, **kargs):
        
        super(LoginPage, self).__init__(*args, **kargs)

        # Strings used in this page
        txtKeyList = ['title', 'back_button_warning',
                      'user_name_text', 'unsupported_warning',
                      'error_blank_name']
        self.textDict.update(self.batchGetText(txtKeyList))

        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = ["validateForm()", ]

    def _getHTMLTxt(self):
        txtBox = """<input type="text" name="%s" value=""/>"""
        productNote = "%s <br /><b><i>%s</i></b><br /><br />\n\n"
        productNote %= (constants.softwareLogo,
                        constants.softwareName)
        
        title = '<div><p id="title">%s</p></div>\n\n' % self.textDict['title']
        
        backButtonWarning = self.textDict['back_button_warning']
        pg0HTML = self.textDict['user_name_text'] + "<br /><br />"
        pg0HTML += (txtBox % 'user_name_init') + "<br /><br />"
        pg0HTML += backButtonWarning
        
        unsupportedWarning = self.textDict['unsupported_warning']
         
        return productNote + title + pg0HTML + unsupportedWarning

    def getValidation(self):
        loginValidation = ('var y=document.forms["languageSurvey"];'
                           ''
                           'if (textBoxValidate(y["user_name_init"])==1)'
                           '{'
                           'alert("%s");'
                           'return false;'
                           '}'
                           'return true;'
                           )
        
        txt = self.textDict['error_blank_name']
        txt = txt.replace('"', "'")
        retPage = loginValidation % txt
        
        return retPage
        
    def getHTML(self):
        htmlText = self._getHTMLTxt()
        pageTemplate = join(self.webSurvey.htmlDir,
                            "blankPageWValidation.html")
    
        embedTxt = "isSupportedBrowser()\n\n"
    
        return htmlText, pageTemplate, {'embed': embedTxt}


class LoginErrorPage(LoginPage):
    
    pageName = "login_bad_user_name"
        
    def __init__(self, userName, *args, **kargs):
        
        super(LoginErrorPage, self).__init__(*args, **kargs)
        
        self.userName = userName
        
        # Strings used in this page
        txtKeyList = ['error_user_name_exists', ]
        self.textDict.update(self.batchGetText(txtKeyList))
        
    def _getHTMLTxt(self):

        pg0HTML = super(LoginErrorPage, self)._getHTMLTxt()
        pg0HTML = pg0HTML
        
        textKey = 'error_user_name_exists'
        userNameErrorTxt = self.textDict[textKey]
    
        if '%s' not in userNameErrorTxt:
            # A warning to the developer, not the user
            errorMsg = ("Please add a '%s' for the user name in the text "
                        "associated with this key")
            raise loader.BadlyFormattedTextError(errorMsg, textKey,
                                                 self.webSurvey.textDict)
        
        pg0HTML += "<br />" + userNameErrorTxt
    
        return pg0HTML
    
    def getHTML(self):
        htmlText = self._getHTMLTxt() % self.userName
        pageTemplate = join(self.webSurvey.htmlDir,
                            "blankPageWValidation.html")
        
        return htmlText, pageTemplate, {}


class ConsentPage(abstract_pages.NonRecordingPage):
    
    pageName = "consent"
    
    def __init__(self, consentName, *args, **kargs):
        
        super(ConsentPage, self).__init__(*args, **kargs)
        
        if consentName is None:
            consentName = "text"
            
        self.consentName = consentName
    
        # Strings used in this page
        txtKeyList = ["title", "consent_title",
                      self.consentName,
                      "consent_query", "consent", "dissent",
                      'error_consent_or_dissent', ]
        self.textDict.update(self.batchGetText(txtKeyList))
    
        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = ["validateForm()", ]
    
    def _getHTMLTxt(self):
        
        fn = join(self.webSurvey.htmlSnippetsDir, "consent.html")
        with io.open(fn, "r", encoding='utf-8') as fd:
            consentText = fd.read()
        consentText %= (self.textDict["title"],
                        self.textDict["consent_title"],
                        self.textDict[self.consentName])
        
        consentText += "\n\n<hr /><br /><br />"
        consentText += self.textDict["consent_query"]
    
        consentButton = html.radioButton % "consent"
        dissentButton = html.radioButton % "dissent"
    
        consentButtonTxt = self.textDict["consent"]
        dissentButtonTxt = self.textDict["dissent"]
        consentChoice = '%s %s\n<br /><br />%s %s'
        consentChoice %= (consentButton, consentButtonTxt,
                          dissentButton, dissentButtonTxt)
    
        consentHTML = consentText + "<br /><br />" + consentChoice
        
        return consentHTML
    
    def getValidation(self):
        txt = self.textDict['error_consent_or_dissent']
        txt = txt.replace('"', "'")
        retPage = checkboxValidation % txt
        
        return retPage
    
    def getHTML(self):
        htmlText = self._getHTMLTxt()
        pageTemplate = join(self.webSurvey.htmlDir,
                            "blankPageWValidation.html")
    
        return htmlText, pageTemplate, {}

    
class ConsentEndPage(abstract_pages.NonValidatingPage):
    
    pageName = "consent_end"
    
    def __init__(self, *args, **kargs):

        super(ConsentEndPage, self).__init__(*args, **kargs)
    
        # Strings used in this page
        txtKeyList = ["consent_opt_out", ]
        self.textDict.update(self.batchGetText(txtKeyList))
    
        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = []
    
    def getHTML(self):
        htmlText = self.textDict['consent_opt_out']
        pageTemplate = join(self.webSurvey.htmlDir, "finalPageTemplate.html")
    
        return htmlText, pageTemplate, {}


class TextPage(abstract_pages.NonValidatingPage):

    pageName = "text_page"
    
    def __init__(self, textName, bindSubmitKeyIDList=None, *args, **kargs):

        super(TextPage, self).__init__(*args, **kargs)
        
        # Normalize variables
        if bindSubmitKeyIDList is not None:
            tmpKeyIDList = html.mapKeylist(bindSubmitKeyIDList)
            bindSubmitKeyIDList = tmpKeyIDList
        
        self.textName = textName
        self.bindSubmitKeyIDList = bindSubmitKeyIDList
    
        # Strings used in this page
        txtKeyList = ['title', self.textName]
        self.textDict.update(self.batchGetText(txtKeyList))
    
        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = []

    def _getKeyPressEmbed(self):
        
        bindKeyTxt = ""

        # Bind key press to play button?
        if self.bindSubmitKeyIDList is not None:
            for _, keyID in enumerate(self.bindSubmitKeyIDList):
                clickJS = 'document.getElementById("submitButton").click();'
                bindTuple = (keyID, clickJS)
                bindKeyTxt += ("\n" + html.bindKeySubSnippetJS % bindTuple)
        
        returnJS = ""
        if bindKeyTxt != "":
            returnJS = html.bindKeyJSTemplate % bindKeyTxt
        
        return returnJS
    
    def _getHTMLTxt(self):
        
        htmlText = ('<p id="title">'
                    '%s'
                    '</p><br /><br />'
                    ''
                    '<div id="longText">'
                    ''
                    '%s'
                    '</div><br />')

        htmlText %= (self.textDict['title'], self.textDict[self.textName])
        
        return htmlText

    def getHTML(self):
        htmlText = self._getHTMLTxt()
        pageTemplate = join(self.webSurvey.htmlDir, "basicTemplate.html")
        
        embedTxt = ""
        embedTxt += self._getKeyPressEmbed()
        
        return htmlText, pageTemplate, {'embed': embedTxt}


class TextAndMediaPage(abstract_pages.NonValidatingPage):
    
    pageName = "text_and_media_page"
    
    def __init__(self, audioOrVideo, minPlays, maxPlays, textName,
                 mediaList, bindSubmitKeyIDList=None, *args, **kargs):
        
        super(TextAndMediaPage, self).__init__(*args, **kargs)
        
        # Normalize variables
        if bindSubmitKeyIDList is not None:
            tmpKeyIDList = html.mapKeylist(bindSubmitKeyIDList)
            bindSubmitKeyIDList = tmpKeyIDList
        
        self.audioOrVideo = audioOrVideo
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        self.textName = textName
        self.mediaList = mediaList
        self.bindSubmitKeyIDList = bindSubmitKeyIDList
        self.wavDir = self.webSurvey.wavDir
        
        assert(audioOrVideo in ["audio", "video"])
        
        # Strings used in this page
        txtKeyList = [self.textName, 'title']
        txtKeyList.extend(abstract_pages.audioTextKeys)
        self.textDict.update(self.batchGetText(txtKeyList))
        
        # Variables that all pages need to define
        self.numAudioButtons = len(mediaList)
        self.processSubmitList = []

    def _getKeyPressEmbed(self):
        
        bindKeyTxt = ""

        # Bind key press to play button?
        if self.bindSubmitKeyIDList is not None:
            for _, keyID in enumerate(self.bindSubmitKeyIDList):
                clickJS = 'document.getElementById("submitButton").click();'
                bindTuple = (keyID, clickJS)
                bindKeyTxt += ("\n" + html.bindKeySubSnippetJS % bindTuple)
        
        returnJS = ""
        if bindKeyTxt != "":
            returnJS = html.bindKeyJSTemplate % bindKeyTxt
        
        return returnJS
    
    def getHTML(self):
        
        audioLabel = self.textDict['play_button']
        mediaNameList = [name.strip() for name in self.mediaList]
        audioButtonList = [audio.generateAudioButton(name, i, audioLabel,
                                                     0, False)
                           for i, name in enumerate(mediaNameList)]
        
        tmpTxt = self.textDict[self.textName] % tuple(audioButtonList)
        htmlText = ('<p id="title">'
                    '%s'
                    '</p><br /><br />'
                    ''
                    '<div id="longText">'
                    ''
                    '%s'
                    ''
                    '</div><br />')
        htmlText %= (self.textDict['title'], tmpTxt)
        
        if self.audioOrVideo == "audio":
            extList = self.webSurvey.audioExtList
        else:
            extList = self.webSurvey.videoExtList
        
        embedTxt = ""
        embedTxt += self._getKeyPressEmbed()
        embedTxt += "\n\n" + audio.generateEmbed(self.wavDir, mediaNameList,
                                                 extList, self.audioOrVideo)
        
        pageTemplate = join(self.webSurvey.htmlDir, "basicTemplate.html")
        
        return htmlText, pageTemplate, {'embed': embedTxt}


class MediaTestPage(abstract_pages.NonRecordingPage):
    
    pageName = "media_test"
    
    def __init__(self, audioOrVideo, mediaName, *args, **kargs):
        super(MediaTestPage, self).__init__(*args, **kargs)
        self.audioOrVideo = audioOrVideo
        self.mediaName = mediaName
        self.wavDir = self.webSurvey.wavDir
    
        assert(audioOrVideo in ["audio", "video"])
    
        # Strings used in this page
        txtKeyList = ["mediaTest_text", "mediaTest_affirm",
                      "mediaTest_reject", 'error_verify_media']
        txtKeyList.extend(abstract_pages.audioTextKeys)
        self.textDict.update(self.batchGetText(txtKeyList))
    
        # Variables that all pages need to define
        self.numAudioButtons = 1
        self.minPlays = 1
        self.maxPlays = -1
        self.listenPartial = True
        self.processSubmitList = ["validateForm()",
                                  "audioLoader.verifyAudioPlayed()"]
    
    def _getHTMLTxt(self):
        
        consentText = "\n\n<hr /><br /><br />"
        consentText += self.textDict["mediaTest_text"]
    
        consentButton = html.radioButton % "consent"
        dissentButton = html.radioButton % "dissent"
    
        audioTestAffirm = self.textDict["mediaTest_affirm"]
        audioTestReject = self.textDict["mediaTest_reject"]
        consentChoice = '%s %s\n<br /><br />%s %s' % (consentButton,
                                                      audioTestAffirm,
                                                      dissentButton,
                                                      audioTestReject)
    
        consentHTML = consentText + "<br /><br />%s<br /><br />"
        consentHTML += consentChoice
    
        return consentHTML
    
    def getValidation(self):
        
        txt = self.textDict['error_verify_media']
        txt = txt.replace('"', "'")
        retPage = checkboxValidation % txt
        
        return retPage
    
    def getHTML(self):
    
        htmlText = self._getHTMLTxt()
        pageTemplate = join(self.webSurvey.htmlDir,
                            "blankPageWValidation.html")
        
        audioLabel = self.textDict['play_button']
        htmlText %= audio.generateAudioButton(self.mediaName, 0, audioLabel,
                                              0, False)
        htmlText += "<br />"
        
        if self.audioOrVideo == "audio":
            extList = self.webSurvey.audioExtList
        else:
            extList = self.webSurvey.videoExtList
        
        embedTxt = ""
        embedTxt += "\n\n" + audio.generateEmbed(self.wavDir,
                                                 [self.mediaName, ],
                                                 extList,
                                                 self.audioOrVideo)
        
        return htmlText, pageTemplate, {'embed': embedTxt}


class MediaTestEndPage(abstract_pages.NonValidatingPage):
    
    pageName = "media_test_end"
    
    def __init__(self, *args, **kargs):
        super(MediaTestEndPage, self).__init__(*args, **kargs)
        
        # Strings used in this page
        txtKeyList = ['mediaTest_no_audio', ]
        self.textDict.update(self.batchGetText(txtKeyList))
        
        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = []
    
    def getHTML(self):
        htmlText = self.textDict['mediaTest_no_audio']
        pageTemplate = join(self.webSurvey.htmlDir, "finalPageTemplate.html")
        
        return htmlText, pageTemplate, {}


class EndPage(abstract_pages.NonValidatingPage):
    
    pageName = "end"
    
    def __init__(self, *args, **kargs):
        super(EndPage, self).__init__(*args, **kargs)
        
        # Strings used in this page
        txtKeyList = ["test_complete"]
        self.textDict.update(self.batchGetText(txtKeyList))
        
        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = []
        
    def getHTML(self):
        htmlText = self.textDict['test_complete']
        pageTemplate = join(self.webSurvey.htmlDir, "finalPageTemplate.html")
    
        return htmlText, pageTemplate, {}
