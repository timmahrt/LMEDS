'''
Created on Mar 1, 2014

@author: tmahrt

Core pages may appear in any LMEDS tests, regardless of what kind of
experiment it is.  Pages that provide information to users, get their
 user name or consent, error pages, etc.
'''

from os.path import join

from lmeds.pages import abstractPages

from lmeds import loader
from lmeds import constants
from lmeds import html
from lmeds import audio

checkboxValidation = """
var y=document.forms["languageSurvey"];
if (checkBoxValidate(y["radio"])==true)
    {
    alert("%s");
    return false;
    }
return true;
"""


class LoginPage(abstractPages.NonRecordingPage):
    
    sequenceName = "login"
    
    def __init__(self, *args, **kargs):
        
        super(LoginPage, self).__init__(*args, **kargs)

        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = ["validateForm", ]

    def _getHTMLTxt(self):
        txtBox = """<input type="text" name="%s" value=""/>"""
        productNote = "%s <br /><b><i>%s</i></b><br /><br />\n\n"
        productNote %= (loader.getText('experiment header'),
                        constants.softwareName)
        
        title = '<div><p id="title">%s</p></div>\n\n' % loader.getText('title')
        
        backButtonWarning = loader.getText('back button warning')
        pg0HTML = loader.getText('user name text') + "<br /><br />"
        pg0HTML += (txtBox % 'user_name_init') + "<br /><br />"
        pg0HTML += backButtonWarning
        
        unsupportedWarning = loader.getText('unsupported warning')
         
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
        
        txt = loader.getText('error blank name')
        txt = txt.replace('"', "'")
        retPage = loginValidation % txt
        
        return retPage
        
    def getHTML(self):
        htmlText = self._getHTMLTxt()
        pageTemplate = join(constants.htmlDir, "blankPageWValidation.html")
    
        embedTxt = html.checkForAudioTag()
    
        return htmlText, pageTemplate, {'embed': embedTxt}


class LoginErrorPage(LoginPage):
    
    sequenceName = "login_bad_user_name"
        
    def __init__(self, userName, *args, **kargs):
        
        super(LoginErrorPage, self).__init__(*args, **kargs)
        
        self.userName = userName
        
    def _getHTMLTxt(self):

        pg0HTML = super(LoginErrorPage, self)._getHTMLTxt()
        pg0HTML = pg0HTML
    
        textKey = 'error user name exists'
        userNameErrorTxt = loader.getText(textKey)
    
        if '%s' not in userNameErrorTxt:
            # A warning to the developer, not the user
            errorMsg = ("Please add a '%s' for the user name in the text "
                        "associated with this key")
            raise loader.BadlyFormattedTextError(errorMsg, textKey)
        
        pg0HTML += "<br />" + userNameErrorTxt
    
        return pg0HTML
    
    def getHTML(self):
        htmlText = self._getHTMLTxt() % self.userName
        pageTemplate = join(constants.htmlDir, "blankPageWValidation.html")
        
        return htmlText, pageTemplate, {}


class ConsentPage(abstractPages.NonRecordingPage):
    
    sequenceName = "consent"
    
    def __init__(self, consentName, *args, **kargs):
        
        super(ConsentPage, self).__init__(*args, **kargs)
        
        if consentName is None:
            consentName = "text"
            
        self.consentName = consentName
    
        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = ["validateForm", ]
    
    def _getHTMLTxt(self):
        
        consentText = open(join(constants.htmlSnippetsDir, "consent.html"),
                           "r").read()
        consentText %= (loader.getText("title"),
                        loader.getText("consent title"),
                        loader.getText("consent %s" % self.consentName))
        
        consentText += "\n\n<hr /><br /><br />"
        consentText += loader.getText("consent query")
    
        consentButton = html.radioButton % "consent"
        dissentButton = html.radioButton % "dissent"
    
        consentButtonTxt = loader.getText("consent")
        dissentButtonTxt = loader.getText("dissent")
        consentChoice = '%s %s\n<br /><br />%s %s'
        consentChoice %= (consentButton, consentButtonTxt,
                          dissentButton, dissentButtonTxt)
    
        consentHTML = consentText + "<br /><br />" + consentChoice
        
        return consentHTML
    
    def getValidation(self):
        txt = loader.getText('error consent or dissent')
        txt = txt.replace('"', "'")
        retPage = checkboxValidation % txt
        
        return retPage
    
    def getHTML(self):
        htmlText = self._getHTMLTxt()
        pageTemplate = join(constants.htmlDir, "blankPageWValidation.html")
    
        return htmlText, pageTemplate, {}

    
class ConsentEndPage(abstractPages.NonValidatingPage):
    
    sequenceName = "consent_end"
    
    def __init__(self, *args, **kargs):

        super(ConsentEndPage, self).__init__(*args, **kargs)
    
        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = []
    
    def getHTML(self):
        htmlText = loader.getText('consent opt out')
        pageTemplate = join(constants.htmlDir, "finalPageTemplate.html")
    
        return htmlText, pageTemplate, {}


class TextPage(abstractPages.NonValidatingPage):

    sequenceName = "text_page"
    
    def __init__(self, textName, *args, **kargs):

        super(TextPage, self).__init__(*args, **kargs)
        self.textName = textName
    
        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = []
    
    def _getHTMLTxt(self):
        
        htmlText = ('<p id="title">'
                    '%s'
                    '</p><br /><br />'
                    ''
                    '<div id="longText">'
                    ''
                    '%s'
                    '</div><br />')

        htmlText %= (loader.getText('title'), loader.getText(self.textName))
        
        return htmlText

    def getHTML(self):
        htmlText = self._getHTMLTxt()
        pageTemplate = join(constants.htmlDir, "basicTemplate.html")
        
        return htmlText, pageTemplate, {}


class TextAndAudioPage(abstractPages.NonValidatingPage):
    
    sequenceName = "text_and_audio_page"
    
    def __init__(self, textName, audioList, *args, **kargs):
        
        super(TextAndAudioPage, self).__init__(*args, **kargs)
        self.textName = textName
        self.audioList = audioList
        self.wavDir = self.webSurvey.wavDir
        
        # Variables that all pages need to define
        self.numAudioButtons = len(audioList)
        self.processSubmitList = []
    
    def getHTML(self):
    
        audioNameList = [name.strip() for name in self.audioList]
        audioButtonList = [audio.generateAudioButton(name, i, 0, False)
                           for i, name in enumerate(audioNameList)]
        
        tmpTxt = loader.getText(self.textName) % tuple(audioButtonList)
        htmlText = ('<p id="title">'
                    '%s'
                    '</p><br /><br />'
                    ''
                    '<div id="longText">'
                    ''
                    '%s'
                    ''
                    '</div><br />')
        htmlText %= (loader.getText('title'), tmpTxt)
        
        embedTxt = audio.getPlaybackJS(True, len(audioNameList), -1, 1)
        embedTxt += "\n\n" + audio.generateEmbed(self.wavDir, audioNameList)
        
        pageTemplate = join(constants.htmlDir, "basicTemplate.html")
        
        return htmlText, pageTemplate, {'embed': embedTxt}


class AudioTestPage(abstractPages.NonRecordingPage):
    
    sequenceName = "audio_test"
    
    def __init__(self, wavName, *args, **kargs):
        super(AudioTestPage, self).__init__(*args, **kargs)
        self.wavName = wavName
        self.wavDir = self.webSurvey.wavDir
    
        # Variables that all pages need to define
        self.numAudioButtons = 1
        self.processSubmitList = ["validateForm", "verifyAudioPlayed"]
    
    def _getHTMLTxt(self):
        
        consentText = "\n\n<hr /><br /><br />"
        consentText += loader.getText("audioTest text")
    
        consentButton = html.radioButton % "consent"
        dissentButton = html.radioButton % "dissent"
    
        audioTestAffirm = loader.getText("audioTest affirm")
        audioTestReject = loader.getText("audioTest reject")
        consentChoice = '%s %s\n<br /><br />%s %s' % (consentButton,
                                                      audioTestAffirm,
                                                      dissentButton,
                                                      audioTestReject)
    
        consentHTML = consentText + "<br /><br />%s<br /><br />"
        consentHTML += consentChoice
    
        return consentHTML
    
    def getValidation(self):
        
        txt = loader.getText('error verify audio')
        txt = txt.replace('"', "'")
        retPage = checkboxValidation % txt
        
        return retPage
    
    def getHTML(self):
    
        htmlText = self._getHTMLTxt()
        pageTemplate = join(constants.htmlDir, "blankPageWValidation.html")
        
        htmlText %= audio.generateAudioButton(self.wavName, 0, 0, False)
        htmlText += "<br />"
        
        embedTxt = audio.getPlaybackJS(True, 1, -1, 1, listenPartial=True)
        embedTxt += "\n\n" + audio.generateEmbed(self.wavDir, [self.wavName, ])
        
        return htmlText, pageTemplate, {'embed': embedTxt}


class AudioTestEndPage(abstractPages.NonValidatingPage):
    
    sequenceName = "audio_test_end"
    
    def __init__(self, *args, **kargs):
        super(AudioTestEndPage, self).__init__(*args, **kargs)
        
        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = []
    
    def getHTML(self):
        htmlText = loader.getText('audioTest no audio')
        pageTemplate = join(constants.htmlDir, "finalPageTemplate.html")
        
        return htmlText, pageTemplate, {}


class EndPage(abstractPages.NonValidatingPage):
    
    sequenceName = "end"
    
    def __init__(self, *args, **kargs):
        super(EndPage, self).__init__(*args, **kargs)
        
        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = []
        
    def getHTML(self):
        htmlText = loader.getText('test complete')
        pageTemplate = join(constants.htmlDir, "finalPageTemplate.html")
    
        return htmlText, pageTemplate, {}
