'''
Created on Mar 1, 2014

@author: tmahrt


'''

from os.path import join

from lmeds.pages import abstractPages

from lmeds import survey
from lmeds import constants
from lmeds import html
from lmeds import loader
from lmeds import audio
from lmeds import utils

# Can be used for axb or ab page validation
abValidation = """
var y=document.forms["languageSurvey"];
if (checkBoxValidate(y["axb"])==true)
  {
  alert("%s");
  return false;
  }
  return true;
"""

class SurveyPage(abstractPages.NonValidatingPage):

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
                itemHTML = "%s) %s<br />%s" % (item.enumStrId, item.text, elementHTML)
            
            if item.depth == 1:
                itemHTML = "<div id='indentedText'>%s</div>" % itemHTML
            elif item.depth > 1:
                itemHTML = "<div id='doubleIndentedText'>%s</div>" % itemHTML
            
            itemHTMLList.append(itemHTML)
        
        surveyHTML = "<br /><br />\n".join(itemHTMLList)
        
        javascript = """document.getElementById("%d").selectedIndex = -1;"""
        javascriptList = [javascript % i for i in choiceBoxIndexList]
    
            
        embedTxt = """\n<script type="text/javascript">\nfunction setchoiceboxes() {
        %s
        }
        window.addEventListener("load", setchoiceboxes);\n</script>\n""" % "\n".join(javascriptList)
        
        htmlTxt = "<div id='longText'>%s</div>" % surveyHTML
        return htmlTxt, embedTxt


    def getOutput(self, form):
        
        def replaceCommas(inputItem):
            if type(inputItem) == type([]):
                outputItem = [inputStr.replace(",", "") for inputStr in inputItem]
            else:
                outputItem = inputItem.replace(",", "")
            return outputItem 
        
        tmpList = []
        k = 0
        
        # Filter out items with no inputs (essentially notes/comments)
        dataFullList = [item for item in self.surveyItemList
                        if not all([row[0] == "None" for row in item.widgetList])]
        
        for j, item in enumerate(dataFullList):
            
            for i, currentItem in enumerate(item.widgetList):
                itemType, argList = currentItem
                
                value = form.getvalue(str(k))
                
                if not value:
                    value = ""
                    if itemType in ["Choice", "Item_List", "Choicebox"]:
                        value = ","*(len(argList)-1) # 1 comma between every element
                else:
                    value = value.decode("utf-8")
                    
                    # Remove newlines (because each newline is a new data entry)
                    if itemType == "Multiline_Textbox":
                        value = replaceCommas(value)
                        newlineChar = utils.detectLineEnding(value)
                        if newlineChar != None:
                            value = value.replace(newlineChar, " - ") 
                            
                    
                    elif itemType in ["Choice", "Choicebox"]:
                        if itemType == "Choice":
                            index = argList.index(value)
                        elif itemType == "Choicebox":
                            index = int(value)
                            
                        valueList = ["0" for x in xrange(len(argList))]
                        valueList[index] = "1"
                        value = ",".join(replaceCommas(valueList))
                        
                    elif itemType in ["Item_List"]:
                        indexList = [argList.index(subVal) for subVal in value]
                        valueList = ["1" if i in indexList else "0" for i in xrange(len(argList))]
                        value = ",".join(replaceCommas(valueList))
                    
                    elif itemType == "None":
                        continue
                
                tmpList.append(value)
                
                k += 1
        
#         tmpList = outputList
        
        return ",".join(tmpList)
    
    
    def getNumOutputs(self):
        return -1 # TODO: Accurately calculate this


    def getHTML(self):
        htmlText, embedTxt = self._getHTMLTxt()
        pageTemplate = join(constants.htmlDir, "basicTemplate.html")
        
        return htmlText, pageTemplate, {'embed':embedTxt}



class ABNPage(abstractPages.AbstractPage):
    
    sequenceName = "abn"
    
    VALIDATION_STRING = "validation_string"
    
    textStringList = [VALIDATION_STRING, ]
    
    def __init__(self, audioName, minPlays, maxPlays, *args, **kargs):
        super(ABNPage, self).__init__(*args, **kargs)
        
        self.audioName = audioName
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        
        self.wavDir = self.webSurvey.wavDir
        
        self.submitProcessButtonFlag = False
        self.nonstandardSubmitProcessList = [('widget', "abn")]
        
        # Variables that all pages need to define
        self.numAudioButtons = 1
        self.processSubmitList = []

    def _getHTMLTxt(self):
        
        radioButton = '<p><input type="radio" name="abn" value="%(id)s" id="%(id)s" disabled /> <label for="%(id)s">.</label></p>'
        
        htmlTxt = """
        %%s
    <table class="center">
    <tr><td>%%s</td><td>%%s</td><td>%%s</td></tr>
    <tr><td>%s</td><td>%s</td><td>%s</td></tr>
    </table>""" 
        
        return htmlTxt % (radioButton % {'id':'0'},
                          radioButton % {'id':'1'},
                          radioButton % {'id':'2'})
        
        
    def getValidation(self):
        abnValidation = """
        var y=document.forms["languageSurvey"];
        if (checkBoxValidate(y["abn"])==true)
          {
          alert("%s");
          return false;
          }
          return true;
        """
        
#         retPage = abnValidation % loader.getText(self.VALIDATION_STRING)#'Error.  Select one of the three options'
        
        return ""
        
    
    def getNumOutputs(self):
        return 3
    
    
    def getHTML(self):
        '''
        Listeners hear one file and decide if its an example of "textA", "textB" or "None"
        '''
        pageTemplate = join(constants.htmlDir, "axbTemplate.html")
        
        aHTML = audio.generateAudioButton(self.audioName, 0, 0, False)
        
        description = loader.getText("abn text")
        
        a = loader.getText("abn a")
        b = loader.getText("abn b")
        n = loader.getText("abn n")
        
        availableFunctions = """<script>
        function enable_checkboxes() {
        document.getElementById("0").disabled=false;
        document.getElementById("1").disabled=false;
        document.getElementById("2").disabled=false;
        }
        function disable_checkboxes() {
        document.getElementById("0").disabled=true;
        document.getElementById("1").disabled=true;
        document.getElementById("2").disabled=true;
        }        
        </script>
        """
        
        htmlText = description + "<br />" + self._getHTMLTxt()
        htmlText %= (aHTML, a, b, n)
        
        embedTxt = audio.getPlayAudioJavaScript(True, 1, self.maxPlays, self.minPlays,
                                                executeOnFinishSnippet="enable_checkboxes();")
        embedTxt += "\n\n" + audio.generateEmbed(self.wavDir, [self.audioName])
        embedTxt += "\n\n" + availableFunctions
    
        return htmlText, pageTemplate, {'embed':embedTxt}


class SameDifferentBeepPage(abstractPages.AbstractPage):
    
    sequenceName = "same_different_beep"
    
    def __init__(self, audioName1, minPlays, maxPlays, *args, **kargs):
        super(SameDifferentBeepPage, self).__init__(*args, **kargs)
        
        self.audioName1 = audioName1
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        
        self.wavDir = self.webSurvey.wavDir

        self.submitProcessButtonFlag = False
        self.nonstandardSubmitProcessList = [('widget', "same_different_beep"),]

        # Variables that all pages need to define
        self.numAudioButtons = 1
        self.processSubmitList = []
        
    
    def _getHTMLTxt(self):
        
        radioButton = '<p><input type="radio" name="same_different_beep" value="%(id)s" id="%(id)s" /> <label for="%(id)s">.</label></p>'
        
        htmlTxt = """
        <br /><br />%%s<br /><br />
    <table class="center">
    <tr><td>%%s</td><td>%%s</td><td>%%s</td></tr>
    <tr><td>%s</td><td>%s</td><td>%s</td></tr>
    </table>""" 
        
        return htmlTxt % (radioButton % {'id':'0'},
                          radioButton % {'id':'1'},
                          radioButton % {'id':'2'},)
    
    
    def getValidation(self):
        txt = loader.getText('error select same or different')
        txt = txt.replace('"', "'")
        retPage = abValidation % txt
        
        return retPage
    
    
    def getNumOutputs(self):
        return 3
    
        
    def getHTML(self):
        '''
        Listeners hear two files and decide if they are the same or different
        '''
        pageTemplate = join(constants.htmlDir, "axbTemplate.html")
        
        aHTML = audio.generateAudioButton(self.audioName1, 0, 0, False)
        
        description = loader.getText("same_different text")
        
        sameTxt = loader.getText("same_different same")
        differentTxt = loader.getText("same_different different")
        beepTxt = loader.getText("same_different beep")
        
        htmlText = description + self._getHTMLTxt()
        htmlText %= (aHTML, sameTxt, differentTxt, beepTxt)
    
        embedTxt = audio.getPlayAudioJavaScript(True, 1, self.maxPlays, self.minPlays)
        embedTxt += "\n\n" + audio.generateEmbed(self.wavDir, self.audioName1)

        return htmlText, pageTemplate, {'embed': embedTxt}
    
    
class SameDifferentPage(abstractPages.AbstractPage):
    
    sequenceName = "same_different"
    
    def __init__(self, audioName1, audioName2, minPlays, maxPlays, *args, **kargs):
        super(SameDifferentPage, self).__init__(*args, **kargs)
        
        self.audioName1 = audioName1
        self.audioName2 = audioName2
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        
        self.wavDir = self.webSurvey.wavDir

        # Variables that all pages need to define
        self.numAudioButtons = 2
        self.processSubmitList = []
        
    
    def _getHTMLTxt(self):
        
        radioButton = '<p><input type="radio" name="same_different" value="%(id)s" id="%(id)s" /> <label for="%(id)s">.</label></p>'
        
        htmlTxt = """
        <br /><br />%%s %%s<br /><br />
    <table class="center">
    <tr><td>%%s</td><td>%%s</td></tr>
    <tr><td>%s</td><td>%s</td></tr>
    </table>""" 
        
        return htmlTxt % (radioButton % {'id':'0'},
                          radioButton % {'id':'1'})
    
    
    def getValidation(self):
        txt = loader.getText('error select same or different')
        txt = txt.replace('"', "'")
        retPage = abValidation % txt
        
        return retPage
    
    
    def getNumOutputs(self):
        return 2
    
        
    def getHTML(self):
        '''
        Listeners hear two files and decide if they are the same or different
        '''
        pageTemplate = join(constants.htmlDir, "axbTemplate.html")
        
        aHTML = audio.generateAudioButton(self.audioName1, 0, 0, False)
        bHTML = audio.generateAudioButton(self.audioName2, 1, 0, False)
        
        description = loader.getText("same_different text")
        
        sameTxt = loader.getText("same_different same")
        differentTxt = loader.getText("same_different different")
        
        htmlText = description + self._getHTMLTxt()
        htmlText %= (aHTML, bHTML, sameTxt, differentTxt)
    
        embedTxt = audio.getPlayAudioJavaScript(True, 2, self.maxPlays, self.minPlays)
        embedTxt += "\n\n" + audio.generateEmbed(self.wavDir, [self.audioName1, self.audioName2])
    
        return htmlText, pageTemplate, {'embed': embedTxt}


class SameDifferentStream(abstractPages.AbstractPage):
    
    sequenceName = "same_different_stream"
    
    def __init__(self, pauseDuration, minPlays, maxPlays, audioList, *args, **kargs):
        super(SameDifferentStream, self).__init__(*args, **kargs)
        
        self.pauseDuration = pauseDuration
        self.audioList = audioList
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        
        self.wavDir = self.webSurvey.wavDir

        self.submitProcessButtonFlag = False
        self.nonstandardSubmitProcessList = [('widget', "same_different_stream")]

        # Variables that all pages need to define
        self.numAudioButtons = 1
        self.processSubmitList = ["verifyAudioPlayed",]
        
    
    def _getHTMLTxt(self):
        
        radioButton = '<p><input type="radio" name="same_different_stream" value="%(id)s" id="%(id)s" disabled /> <label for="%(id)s">.</label></p>'
        
        htmlTxt = """
        <br /><br />%%s<br /><br />
    <table class="center">
    <tr><td>%%s</td><td>%%s</td></tr>
    <tr><td>%s</td><td>%s</td></tr>
    </table>""" 
        
        return htmlTxt % (radioButton % {'id':'0'},
                          radioButton % {'id':'1'})
    
    
    def getValidation(self):
        txt = loader.getText('error select same or different')
        txt = txt.replace('"', "'")
        retPage = abValidation % txt
        
        return retPage
    
    
    def getNumOutputs(self):
        return 2
    
        
    def getHTML(self):
        '''
        Listeners hear two files and decide if they are the same or different
        '''
        pageTemplate = join(constants.htmlDir, "axbTemplate.html")
        
        availableFunctions = """<script>
        function enable_checkboxes() {
        document.getElementById("0").disabled=false;
        document.getElementById("1").disabled=false;
        }
        function disable_checkboxes() {
        document.getElementById("0").disabled=true;
        document.getElementById("1").disabled=true;
        }        
        </script>
        """
        
        embedTxt = audio.getPlayAudioJavaScript(True, 1, self.maxPlays, self.minPlays,
                                                executeOnFinishSnippet="enable_checkboxes();")
        embedTxt += "\n\n" + audio.generateEmbed(self.wavDir, list(set(self.audioList)))
        embedTxt += "\n\n" + availableFunctions
        
        description = loader.getText("same_different_question")
        
        sameTxt = loader.getText("same_different_same")
        differentTxt = loader.getText("same_different_different")
        
        htmlText = description + self._getHTMLTxt()
        htmlText %= (audio.generateAudioButton(self.audioList, 0, self.pauseDuration, False) + "<br />",
                     sameTxt, differentTxt)
    
        return htmlText, pageTemplate, {'embed': embedTxt}
    
    
class ABPage(abstractPages.AbstractPage):
    
    sequenceName = "ab"
    
    def __init__(self, audioName, minPlays, maxPlays, *args, **kargs):
        super(ABPage, self).__init__(*args, **kargs)
        
        self.audioName = audioName
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        
        self.wavDir = self.webSurvey.wavDir

        # Variables that all pages need to define
        self.numAudioButtons = 1
        self.processSubmitList = ["validateForm",]
        
    
    def _getHTMLTxt(self):
        
        radioButton = '<p><input type="radio" name="ab" value="%(id)s" id="%(id)s" /> <label for="%(id)s">.</label></p>'
        
        htmlTxt = """Write statement about how the user should select (A) or (B).<br /><br />
    <table class="center">
    <tr><td>A</td><td>B</td></tr>
    <tr><td>%%s</td><td>%%s</td></tr>
    <tr><td>%s</td><td>%s</td></tr>
    </table>"""
        htmlTxt %= (radioButton % {'id':'0'}, 
                 radioButton % {'id':'1'})
        
        return htmlTxt 
    
    
    def getValidation(self):
        txt = loader.getText('error select a or b')
        txt = txt.replace('"', "'")
        retPage = abValidation % txt
        
        return retPage
    
    
    def getNumOutputs(self):
        return 2
    
    
    def getHTML(self):
        '''
        Listeners hear one file and decide if its an example of "textA", "textB" or "None"
        '''
        pageTemplate = join(constants.htmlDir, "axbTemplate.html")
        
        aHTML = audio.generateAudioButton(self.audioName, 0, 0, False)
        
        description = loader.getText("abn text")
        
        a = loader.getText("abn a")
        b = loader.getText("abn b")
        n = loader.getText("abn n")
        
        htmlText = description + "<br />" + self.getHTML()
        htmlText %= (aHTML, a, b, n)
        
        embedTxt = audio.getPlayAudioJavaScript(True, 1, self.maxPlays, self.minPlays)
        embedTxt += "\n\n" + audio.generateEmbed(self.wavDir, [self.audioName])
    
        return htmlText, pageTemplate, {'embed':embedTxt}  


class AXBPage(abstractPages.AbstractPage):
    
    sequenceName = "axb"

    def __init__(self,sourceNameX, compareNameA, compareNameB, 
                 minPlays, maxPlays, *args, **kargs):
        
        super(AXBPage, self).__init__(*args, **kargs)
        
        self.sourceNameX = sourceNameX
        self.compareNameA = compareNameA
        self.compareNameB = compareNameB
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        
        self.wavDir = self.webSurvey.wavDir

        # Variables that all pages need to define
        self.numAudioButtons = 3
        self.processSubmitList = ["verifyAudioPlayed", "validateForm",]
        
    
    def _getHTMLTxt(self):
    
        radioButton = '<p><input type="radio" name="axb" value="%(id)s" id="%(id)s" /> <label for="%(id)s">.</label></p>'
        
        htmlTxt = """%s<br /><br /><br />
    %s<br /> <br />
    %%s<br /> <br />
    <table class="center">
    <tr><td>%s</td><td>%s</td></tr>
    <tr><td>%%s</td><td>%%s</td></tr>
    <tr><td>%s</td><td>%s</td></tr>
    </table>"""
        htmlTxt %= (loader.getText("axb query"),
                 loader.getText("axb x"),
                 loader.getText("axb a"),
                 loader.getText("axb b"),
                 radioButton % {'id':'0'}, 
                 radioButton % {'id':'1'})
        
    #     html %= ('<p><input type="radio" value="A" id="A" name="gender" /> <label for="A">Male</label></p>',
    #             '<p><input type="radio" value="B" id="B" name="gender" /> <label for="B ">Female</label></p>')
        
        return htmlTxt    


    def getValidation(self):
        txt = loader.getText('error select a or b')
        txt = txt.replace('"', "'")
        retPage = abValidation % txt
        
        return retPage
    
    
    def getNumOutputs(self):
        return 2
    
    
    def getHTML(self):
        pageTemplate = join(constants.htmlDir, "axbTemplate.html")
        
        xHTML = audio.generateAudioButton(self.sourceNameX, 0, 0, False)
        aHTML = audio.generateAudioButton(self.compareNameA, 1, 0, False)
        bHTML = audio.generateAudioButton(self.compareNameB, 2, 0, False)
        
        htmlText = self._getHTMLTxt()
        htmlText %= (xHTML, aHTML, bHTML)
        
        embedTxt = audio.getPlayAudioJavaScript(True, 3, self.maxPlays, self.minPlays)
        embedTxt += "\n\n" + audio.generateEmbed(self.wavDir, [self.sourceNameX, self.compareNameA, self.compareNameB])
        
        htmlText = html.makeNoWrap(htmlText)
        
        return htmlText, pageTemplate, {'embed':embedTxt}


class AudioListPage(abstractPages.AbstractPage):

    sequenceName = "audio_list"

    def __init__(self, pauseDuration, minPlays, maxPlays, audioList, *args, **kargs):
        super(AudioListPage, self).__init__(*args, **kargs)
        self.pauseDuration = pauseDuration
        self.audioList = audioList
        self.minPlays = minPlays
        self.maxPlays = maxPlays
    
    
        self.wavDir = self.webSurvey.wavDir

        self.submitProcessButtonFlag = False

        # Variables that all pages need to define
        self.numAudioButtons = 1 # Although there are many files, there is just one button 
        self.processSubmitList = ["verifyAudioPlayed",]
        
    
    def _getHTMLTxt(self):
        return "%s<br /><br />"
    
    
    def getValidation(self):
        return 
    
    
    def getNumOutputs(self):
        return 0
    
    
    def getHTML(self):
    
        htmlText = self._getHTMLTxt()
        pageTemplate = join(constants.htmlDir, "axbTemplate.html")
        
        htmlText %= audio.generateAudioButton(self.audioList, 0, 
                                              self.pauseDuration, False) + "<br />"
        
        embedTxt = audio.getPlayAudioJavaScript(True, 1, self.maxPlays, 
                                                self.minPlays, autosubmitFlag=True)
        embedTxt += "\n\n" + audio.generateEmbed(self.wavDir, list(set(self.audioList)))
        
        return htmlText, pageTemplate, {'embed':embedTxt}


class MemoryPage(abstractPages.AbstractPage):
    
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
        self.processSubmitList = ["verifyAudioPlayed", "validateForm",]


    def _getHTMLTxt(self):
        
        radioButton = '<p><input type="radio" name="memory_test" value="%(id)s" id="%(id)s" /> <label for="%(id)s">.</label></p>'
        
        htmlTxt = """
        %%s
    <table class="center">
    <tr><td>%%s</td><td>%%s</td></tr>
    <tr><td>%s</td><td>%s</td></tr>
    </table>""" 
        
        return htmlTxt % (radioButton % {'id':'0'},
                          radioButton % {'id':'1'},)
        
        
    def getValidation(self):
        abnValidation = """
        var y=document.forms["languageSurvey"];
        if (checkBoxValidate(y["memory_test"])==true)
          {
          alert("%s");
          return false;
          }
          return true;
        """
        
#         retPage = abnValidation % loader.getText(self.VALIDATION_STRING)#'Error.  Select one of the three options'
        
        return ""
        
    
    def getNumOutputs(self):
        return 2
    
    
    def getHTML(self):
        '''
        Listeners hear one file and decide if its an example of "textA", "textB" or "None"
        '''
        pageTemplate = join(constants.htmlDir, "axbTemplate.html")
        
        if self.showAudio:
            aHTML = audio.generateAudioButton(self.name, 0, 0, False)
        else:
            aHTML = ""
        
        description = loader.getText("memory_instruct")
        
        a = loader.getText("memory_a")
        b = loader.getText("memory_b")
        
        txtFN = join(self.txtDir, self.name+".txt")
        
        sentenceList = loader.loadTxt(txtFN)
        sentenceTxt = "\n".join(sentenceList)
        
        htmlText = "<i>" + description + "</i><br /><br />" + sentenceTxt + "<br /><br />"  + self._getHTMLTxt()
        htmlText %= (aHTML, a, b)
        
        if self.showAudio:
            embedTxt = audio.getPlayAudioJavaScript(True, 1, self.maxPlays,
                                                    self.minPlays)
            embedTxt += "\n\n" + audio.generateEmbed(self.wavDir, [self.name])
        else:
            embedTxt = ""
    
        return htmlText, pageTemplate, {'embed':embedTxt}
    

class FillInTheBlankPage(abstractPages.AbstractPage):
    
    sequenceName = "fill_in_the_blank"
    
    VALIDATION_STRING = "three_option_validation"
    
    textStringList = [VALIDATION_STRING, ]
    
    def __init__(self, name, timeout, answer1, answer2, answer3, *args, **kargs):
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
        
        radioButton = '<p><input type="radio" name="fill_in_the_blank" value="%(id)s" id="%(id)s" /> <label for="%(id)s">.</label></p>'
        
        htmlTxt = """
    <table class="center">
    <tr><td>%%s</td><td>%%s</td><td>%%s</td></tr>
    <tr><td>%s</td><td>%s</td><td>%s</td></tr>
    </table>""" 
        
        return htmlTxt % (radioButton % {'id':'0'},
                          radioButton % {'id':'1'},
                          radioButton % {'id':'2'})
        
        
    def getValidation(self):
        abnValidation = """
        var y=document.forms["languageSurvey"];
        if (checkBoxValidate(y["fill_in_the_blank"])==true)
          {
          alert("%s");
          return false;
          }
          return true;
        """
        
        retPage = abnValidation % loader.getText(self.VALIDATION_STRING)#'Error.  Select one of the three options'
        
        return retPage
        
    
    def getNumOutputs(self):
        return 3


    def getOutput(self, form):
        return abstractPages.getoutput(self.sequenceName, form, True)
    
    
    def getHTML(self):
        '''
        Listeners hear one file and decide if its an example of "textA", "textB" or "None"
        '''
        pageTemplate = join(constants.htmlDir, "axbTemplate.html")
        
        description = loader.getText("fill_in_the_blank_instruct")
        
        a = self.answer1
        b = self.answer2
        c = self.answer3
        
        txtFN = join(self.txtDir, self.name+".txt")
        
        sentenceList = loader.loadTxt(txtFN)
        sentenceTxt = "\n".join(sentenceList)
        
        htmlText = "<i>" + description + "</i><br /><br />" + sentenceTxt + "<br /><br />"  + self._getHTMLTxt()
        htmlText %= (a, b, c)
        
    
        return htmlText, pageTemplate, {'embed':""}

