'''
Created on Mar 1, 2014

@author: tmahrt


'''

import types
from os.path import join

from lmeds.pages import abstract_pages

from lmeds import survey
from lmeds import constants
from lmeds import html
from lmeds import loader
from lmeds import audio
from lmeds import utils


class SurveyPage(abstract_pages.NonValidatingPage):

    sequenceName = "survey"
    
    def __init__(self, surveyName, *args, **kargs):
        super(SurveyPage, self).__init__(*args, **kargs)
        
        self.surveyFN = surveyName + ".txt"
        self.surveyRoot = self.webSurvey.surveyRoot
        
        # Variables that all pages need to define
        self.numAudioButtons = 0
        self.processSubmitList = []

        self.surveyItemList = survey.parseSurveyFile(join(self.surveyRoot,
                                                          self.surveyFN))

    def _getHTMLTxt(self):
        
        i = 0
        itemHTMLList = []
        
        choiceBoxIndexList = []
        for item in self.surveyItemList:
            
            itemElementList = []
            for dataTuple in item.widgetList:
                elementType, argList = dataTuple
                if elementType == "None":
                    widget = " "
                else:
                    widget = html.createWidget(elementType, argList, i)[0]
                itemElementList.append(widget)
            
                if elementType == "None":
                    continue
                
                if elementType == "Choicebox":
                    choiceBoxIndexList.append(i)
                i += 1
            
            elementHTML = " ".join(itemElementList)
            
            if elementHTML.strip() == "":
                itemHTML = "%s" % item.text
            else:
                itemHTML = "%s) %s<br />%s"
                itemHTML %= (item.enumStrId, item.text, elementHTML)
            
            if item.depth == 1:
                itemHTML = "<div id='indentedText'>%s</div>" % itemHTML
            elif item.depth > 1:
                itemHTML = "<div id='doubleIndentedText'>%s</div>" % itemHTML
            
            itemHTMLList.append(itemHTML)
        
        surveyHTML = "<br /><br />\n".join(itemHTMLList)
        
        javascript = """document.getElementById("%d").selectedIndex = -1;"""
        javascriptList = [javascript % i for i in choiceBoxIndexList]
        
        embedTxt = ('\n<script type="text/javascript">\n'
                    'function setchoiceboxes() {\n'
                    '%s\n'
                    '}\n'
                    'window.addEventListener("load", setchoiceboxes);\n'
                    '</script>\n')
        embedTxt %= "\n".join(javascriptList)
        
        htmlTxt = "<div id='longText'>%s</div>" % surveyHTML
        return htmlTxt, embedTxt
    
    def getOutput(self, form):
        
        def replaceCommas(inputItem):
            if isinstance(inputItem, types.ListType):
                outputItem = [inputStr.replace(",", "")
                              for inputStr in inputItem]
            else:
                outputItem = inputItem.replace(",", "")
            return outputItem
        
        tmpList = []
        k = 0
        
        # Filter out items with no inputs (essentially notes/comments)
        dataFullList = [item for item in self.surveyItemList
                        if not all([row[0] == "None"
                                    for row in item.widgetList])]
        
        for item in dataFullList:
            
            for i, currentItem in enumerate(item.widgetList):
                itemType, argList = currentItem
                
                value = form.getvalue(str(k))
                
                if not value:
                    value = ""
                    if itemType in ["Choice", "Item_List", "Choicebox"]:
                        # 1 comma between every element
                        value = "," * (len(argList) - 1)
                else:
                    value = value.decode("utf-8")
                    
                    # Remove newlines
                    # (because each newline is a new data entry)
                    if itemType == "Multiline_Textbox":
                        value = replaceCommas(value)
                        newlineChar = utils.detectLineEnding(value)
                        if newlineChar is not None:
                            value = value.replace(newlineChar, " - ")
                    
                    elif itemType in ["Choice", "Choicebox"]:
                        if itemType == "Choice":
                            index = argList.index(value)
                        elif itemType == "Choicebox":
                            index = int(value)
                            
                        valueList = ["0", ] * len(argList)
                        valueList[index] = "1"
                        value = ",".join(replaceCommas(valueList))
                        
                    elif itemType in ["Item_List"]:
                        indexList = [argList.index(subVal) for subVal in value]
                        valueList = ["1" if i in indexList else "0"
                                     for i in xrange(len(argList))]
                        value = ",".join(replaceCommas(valueList))
                    
                    elif itemType == "None":
                        continue
                
                tmpList.append(value)
                
                k += 1
        
#         tmpList = outputList
        
        return ",".join(tmpList)
    
    def getNumOutputs(self):
        return -1  # TODO: Accurately calculate this

    def getHTML(self):
        htmlText, embedTxt = self._getHTMLTxt()
        pageTemplate = join(constants.htmlDir, "basicTemplate.html")
        
        return htmlText, pageTemplate, {'embed': embedTxt}


class AudioWithResponsePage(abstract_pages.AbstractPage):
    
    sequenceName = "audio_with_response_page"
    
    VALIDATION_STRING = "audio_with_response_validation_string"
    
    def __init__(self, timeout, audioList, *args, **kargs):
        super(AudioWithResponsePage, self).__init__(*args, **kargs)
        self.audioList = audioList
        self.minPlays = 1
        self.maxPlays = 1
        self.txtboxCols = 100
        self.txtboxRows = 10
        self.pauseDuration = 0
        self.timeout = float(timeout)
        
        self.wavDir = self.webSurvey.wavDir
        self.submitProcessButtonFlag = True
        
        self.numAudioButtons = 1
        self.processSubmitList = []
    
    def _getHTMLTxt(self):
        txtbox = ('<textarea name="audio_with_response_page" '
                  'id="audio_with_response_page" rows="%s" cols="%s" '
                  'disabled></textarea>')
        txtbox %= (self.txtboxRows, self.txtboxCols)
        
        return """%s<br /><br />""" + txtbox
    
    def getValidation(self):
        pass
#         abnValidation = """
#         var y=document.forms["languageSurvey"];
#         if (checkBoxValidate(y["audio_with_response_page"])==true)
#           {
#           alert("%s");
#           return false;
#           }
#           return true;
#         """
#
#         #'Error.  Select one of the three options'
#         retPage = abnValidation % loader.getText(self.VALIDATION_STRING)
        
        return
    
    def getNumOutputs(self):
        return 1
    
    def getHTML(self):
    
        htmlText = self._getHTMLTxt()
        pageTemplate = join(constants.htmlDir, "axbTemplate.html")
        
        htmlText %= audio.generateAudioButton(self.audioList, 0,
                                              self.pauseDuration,
                                              False) + "<br />"
        
        jsFuncs = ('<script>\n'
                   'function enable_textbox() {\n'
                   'document.getElementById("audio_with_response_page"'
                   ').disabled=false;\n'
                   'document.getElementById("audio_with_response_page"'
                   ').focus();\n'
                   '}\n'
                   '</script>\n'
                   )
        
        timeoutJS = "setTimeout(function(){processSubmit()}, %d);"
        timeoutJS %= int(self.timeout * 1000)
        runOnFinishJS = "enable_textbox();" + timeoutJS
        embedTxt = audio.getPlaybackJS(True, 1, self.maxPlays, self.minPlays,
                                       runOnFinish=runOnFinishJS)
        embedTxt += "\n\n" + audio.generateEmbed(self.wavDir,
                                                 list(set(self.audioList)))
        embedTxt += jsFuncs
        
        return htmlText, pageTemplate, {'embed': embedTxt}
    
    def getOutput(self, form):
        
        try:
            # Only one item
            value = form.getlist("audio_with_response_page")[0]
            value = value.decode("utf-8")
        except IndexError:
            value = ""  # They didn't enter anything
        value = value.replace(",", ";")
        newlineChar = utils.detectLineEnding(value)
        if newlineChar is not None:
            value = value.replace(newlineChar, " - ")
        
        return value


class TextResponsePage(abstract_pages.AbstractPage):
    
    sequenceName = "text_response_page"
    
    def __init__(self, timeout, *args, **kargs):
        super(TextResponsePage, self).__init__(*args, **kargs)
        self.txtboxCols = 100
        self.txtboxRows = 10
        self.timeout = float(timeout)
        
        self.submitProcessButtonFlag = True
        
        self.nonstandardSubmitProcessList = []
        if timeout > 0:
            self.nonstandardSubmitProcessList.append(('timeout',
                                                      int(self.timeout)))
        
        self.numAudioButtons = 0
        self.processSubmitList = []

    def _getHTMLTxt(self):
        txtbox = ('<textarea name="audio_with_response_page" '
                  'id="audio_with_response_page" rows="%s" cols="%s">'
                  '</textarea>'
                  )
        txtbox %= (self.txtboxRows, self.txtboxCols)
        
        return txtbox
    
    def getValidation(self):
        return
    
    def getNumOutputs(self):
        return 1
    
    def getHTML(self):
        htmlText = self._getHTMLTxt()
        pageTemplate = join(constants.htmlDir, "axbTemplate.html")
        
        return htmlText, pageTemplate, {}
    
    def getOutput(self, form):
        try:
            # Only one item
            value = form.getlist("audio_with_response_page")[0]
            value = value.decode("utf-8")
        except IndexError:
            value = ""  # They didn't enter anything
        value = value.replace(",", ";")
        newlineChar = utils.detectLineEnding(value)
        if newlineChar is not None:
            value = value.replace(newlineChar, " - ")
        
        return value

    
class AudioListPage(abstract_pages.AbstractPage):

    sequenceName = "audio_list"

    def __init__(self, pauseDuration, minPlays, maxPlays, audioList,
                 *args, **kargs):
        super(AudioListPage, self).__init__(*args, **kargs)
        self.pauseDuration = pauseDuration
        self.audioList = audioList
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        
        self.wavDir = self.webSurvey.wavDir

        self.submitProcessButtonFlag = False

        # Variables that all pages need to define
        
        # Although there are many files, there is just one button
        self.numAudioButtons = 1
        self.processSubmitList = ["verifyAudioPlayed", ]
    
    def _getHTMLTxt(self):
        return "%s<br /><br />"
    
    def getValidation(self):
        return
    
    def getNumOutputs(self):
        return 0
    
    def getHTML(self):
    
        htmlText = self._getHTMLTxt()
        pageTemplate = join(constants.htmlDir, "axbTemplate.html")
        
        htmlText %= audio.generateAudioButton(self.audioList,
                                              0,
                                              self.pauseDuration,
                                              False) + "<br />"
        
        embedTxt = audio.getPlaybackJS(True, 1, self.maxPlays, self.minPlays,
                                       autosubmit=True)
        embedTxt += "\n\n" + audio.generateEmbed(self.wavDir,
                                                 list(set(self.audioList)))
        
        return htmlText, pageTemplate, {'embed': embedTxt}


class MemoryPage(abstract_pages.AbstractPage):
    
    sequenceName = "memory_test"
    
    VALIDATION_STRING = "validation_string"
    
    textStringList = []
    
    def __init__(self, name, minPlays, maxPlays, showAudio, *args, **kargs):
        super(MemoryPage, self).__init__(*args, **kargs)
        
        self.name = name
        
        if showAudio == "False":
            minPlays = 0
            maxPlays = 0
            showAudio = False
        else:
            showAudio = True
            
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        self.showAudio = showAudio
        
        self.wavDir = self.webSurvey.wavDir
        self.txtDir = self.webSurvey.txtDir
        
        # Variables that all pages need to define
        self.numAudioButtons = 1
        self.processSubmitList = ["verifyAudioPlayed", "validateForm", ]

    def _getHTMLTxt(self):
        
        radioButton = ('<p>'
                       '<input type="radio" name="memory_test" '
                       'value="%(id)s" id="%(id)s" /> '
                       '<label for="%(id)s">.</label>'
                       '</p>'
                       )
        
        htmlTxt = ('%%s'
                   '<table class="center">'
                   '<tr><td>%%s</td><td>%%s</td></tr>'
                   '<tr><td>%s</td><td>%s</td></tr>'
                   '</table>'
                   )
        
        return htmlTxt % (radioButton % {'id': '0'},
                          radioButton % {'id': '1'},)
        
    def getValidation(self):
        abnValidation = ('var y=document.forms["languageSurvey"];\n'
                         'if (checkBoxValidate(y["memory_test"])==true)\n'
                         '{\n'
                         'alert("%s");\n'
                         'return false;\n'
                         '}\n'
                         'return true;\n'
                         )
        
#         #  'Error.  Select one of the three options'
#         retPage = abnValidation % loader.getText(self.VALIDATION_STRING)
        
        return ""
    
    def getNumOutputs(self):
        return 2
    
    def getHTML(self):
        '''
        Listeners hear one file and decide if its one of three choices
        
        The choices are "textA", "textB" or "None"
        '''
        pageTemplate = join(constants.htmlDir, "axbTemplate.html")
        
        if self.showAudio:
            aHTML = audio.generateAudioButton(self.name, 0, 0, False)
        else:
            aHTML = ""
        
        description = loader.getText("memory_instruct")
        
        a = loader.getText("memory_a")
        b = loader.getText("memory_b")
        
        txtFN = join(self.txtDir, self.name + ".txt")
        
        sentenceList = loader.loadTxt(txtFN)
        sentenceTxt = "\n".join(sentenceList)
        
        htmlText = "<i>" + description + "</i><br /><br />" + sentenceTxt
        htmlText += "<br /><br />" + self._getHTMLTxt()
        htmlText %= (aHTML, a, b)
        
        if self.showAudio:
            embedTxt = audio.getPlaybackJS(True, 1, self.maxPlays,
                                           self.minPlays)
            embedTxt += "\n\n" + audio.generateEmbed(self.wavDir, [self.name])
        else:
            embedTxt = ""
    
        return htmlText, pageTemplate, {'embed': embedTxt}
    

class FillInTheBlankPage(abstract_pages.AbstractPage):
    
    sequenceName = "fill_in_the_blank"
    
    VALIDATION_STRING = "three_option_validation"
    
    textStringList = [VALIDATION_STRING, ]
    
    def __init__(self, name, timeout, answer1, answer2, answer3,
                 *args, **kargs):
        super(FillInTheBlankPage, self).__init__(*args, **kargs)
        
        self.name = name
        
        self.answer1 = answer1.replace("_", " ")
        self.answer2 = answer2.replace("_", " ")
        self.answer3 = answer3.replace("_", " ")
        
        self.txtDir = self.webSurvey.txtDir
        
        self.submitProcessButtonFlag = False
        self.nonstandardSubmitProcessList = [('timeout', timeout),
                                             ('widget', "fill_in_the_blank")]
        
        # Variables that all pages need to define
        self.processSubmitList = []
        self.numAudioButtons = 0

    def _getHTMLTxt(self):
        
        radioButton = ('<p><input type="radio" name="fill_in_the_blank" '
                       'value="%(id)s" id="%(id)s" />\n'
                       '<label for="%(id)s">.</label>\n'
                       '</p>\n'
                       )
        
        htmlTxt = ('<table class="center">\n'
                   '<tr><td>%%s</td><td>%%s</td><td>%%s</td></tr>\n'
                   '<tr><td>%s</td><td>%s</td><td>%s</td></tr>\n'
                   '</table>\n'
                   )
        
        return htmlTxt % (radioButton % {'id': '0'},
                          radioButton % {'id': '1'},
                          radioButton % {'id': '2'})
    
    def getValidation(self):
        validation = ('var y=document.forms["languageSurvey"];\n'
                      'if (checkBoxValidate(y["fill_in_the_blank"])==true)\n'
                      '{\n'
                      'alert("%s");\n'
                      'return false;\n'
                      '}\n'
                      'return true;\n'
                      )
        
        #  'Error.  Select one of the three options'
        retPage = validation % loader.getText(self.VALIDATION_STRING)
        
        return retPage
    
    def getNumOutputs(self):
        return 3

    def getOutput(self, form):
        return abstract_pages.getoutput(self.sequenceName, form, True)
    
    def getHTML(self):
        '''
        Listeners hear one file and decide if its one of three options
        
        The three options are: "textA", "textB" or "None"
        '''
        pageTemplate = join(constants.htmlDir, "axbTemplate.html")
        
        description = loader.getText("fill_in_the_blank_instruct")
        
        a = self.answer1
        b = self.answer2
        c = self.answer3
        
        txtFN = join(self.txtDir, self.name + ".txt")
        
        sentenceList = loader.loadTxt(txtFN)
        sentenceTxt = "\n".join(sentenceList)
        
        htmlText = "<i>" + description + "</i><br /><br />" + sentenceTxt
        htmlText += "<br /><br />" + self._getHTMLTxt()
        htmlText %= (a, b, c)
        
        return htmlText, pageTemplate, {'embed': ""}
