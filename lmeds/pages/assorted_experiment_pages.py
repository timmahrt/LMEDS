'''
Created on Mar 1, 2014

@author: tmahrt


'''

from os.path import join

from lmeds.pages import abstract_pages

from lmeds.lmeds_io import survey
from lmeds.lmeds_io import loader
from lmeds.code_generation import html
from lmeds.code_generation import audio
from lmeds.utilities import constants
from lmeds.utilities import utils


class SurveyPage(abstract_pages.NonValidatingPage):

    pageName = "survey"
    
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
        
        embedTxt = 'window.addEventListener("load", setchoiceboxes);\n'
        
        htmlTxt = "<div id='longText'>%s</div>" % surveyHTML
        return htmlTxt, embedTxt
    
    def getOutput(self, form):
        
        def replaceCommas(inputItem):
            if isinstance(inputItem, constants.list):
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
                    if itemType not in ["Item_List"]:
                        value = utils.decodeUnicode(value)
                        value = replaceCommas(value)
                        
                    # Remove newlines
                    # (because each newline is a new data entry)
                    if itemType == "Multiline_Textbox":
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
                        if isinstance(value, list):
                            value = [utils.decodeUnicode(subval)
                                     for subval in value]
                        else:
                            value = [utils.decodeUnicode(value), ]
                        
                        indexList = [argList.index(subVal) for subVal in value]
                        valueList = ["1" if i in indexList else "0"
                                     for i in range(len(argList))]
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
        pageTemplate = join(self.webSurvey.htmlDir, "basicTemplate.html")
        
        return htmlText, pageTemplate, {'embed': embedTxt}


class UnbalancedListPair(Exception):
    
    def __init__(self, listA, listB):
        super(UnbalancedListPair, self).__init__()
        self.listA = listA
        self.listB = listB
        
    def __str__(self):
        errStr = "Lists '%s' and '%s' much have the same number of members"
        return errStr % (str(self.listA), str(self.listB))

    
class MediaChoicePage(abstract_pages.AbstractPage):
    
    pageName = "media_choice"
    
    def __init__(self, instructionText, audioOrVideo, pauseDuration,
                 minPlays, maxPlays, mediaListOfLists, responseButtonList,
                 mediaButtonLabelList=None, transcriptList=None,
                 bindPlayKeyIDList=None, bindResponseKeyIDList=None,
                 timeout=None,
                 *args, **kargs):
        super(MediaChoicePage, self).__init__(*args, **kargs)
        
        # Normalize variables
        if bindPlayKeyIDList is not None:
            tmpKeyIDList = html.mapKeylist(bindPlayKeyIDList)
            bindPlayKeyIDList = tmpKeyIDList
        
        if bindResponseKeyIDList is not None:
            tmpKeyIDList = html.mapKeylist(bindResponseKeyIDList)
            bindResponseKeyIDList = tmpKeyIDList
        
        self.instructionText = instructionText
        self.pauseDuration = pauseDuration
        self.mediaList = mediaListOfLists
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        self.responseButtonList = responseButtonList
        self.bindPlayKeyIDList = bindPlayKeyIDList
        self.bindResponseKeyIDList = bindResponseKeyIDList
        self.timeout = None
        
        self.playOnMinList = ['enable_checkboxes', ]
        
        if bindPlayKeyIDList is not None:
            assert(len(mediaListOfLists) == len(bindPlayKeyIDList))
        
        if bindResponseKeyIDList is not None:
            assert(len(responseButtonList) == len(bindResponseKeyIDList))
        
        assert(audioOrVideo in ["audio", "video"])
        self.audioOrVideo = audioOrVideo
        self.buttonLabelList = mediaButtonLabelList
        self.transcriptList = transcriptList
        if transcriptList is not None:
            assert(len(mediaListOfLists) == len(transcriptList))
        
        self.wavDir = self.webSurvey.wavDir
        self.txtDir = self.webSurvey.txtDir
        
        self.submitProcessButtonFlag = False
        self.nonstandardSubmitProcessList = [('widget',
                                              'media_choice')]
        
        if timeout is not None:
            self.nonstandardSubmitProcessList.append(('timeout', timeout))
        
        # Strings used in this page
        txtKeyList = [instructionText, ]
        txtKeyList += responseButtonList
        txtKeyList += _buttonLabelCheck(mediaListOfLists, mediaButtonLabelList)
        
        txtKeyList.extend(abstract_pages.audioTextKeys)
        self.textDict.update(self.batchGetText(txtKeyList))
        
        self.numAudioButtons = len(mediaListOfLists)
        if all([len(subList) == 0 for subList in mediaListOfLists]):
            self.numAudioButtons = 0
        
        self.processSubmitList = []
        if self.numAudioButtons > 0:
            self.processSubmitList.append("audioLoader.verifyAudioPlayed()")

    def _getKeyPressEmbed(self):
        
        bindKeyTxt = ""

        # Bind key press to play button?
        if self.bindPlayKeyIDList is not None:
            for i, keyID in enumerate(self.bindPlayKeyIDList):
                clickJS = 'document.getElementById("button%d").click();' % i
                bindTuple = (keyID, clickJS)
                bindKeyTxt += ("\n" + html.bindKeySubSnippetJS % bindTuple)
            
        # Bind key press to submit event?
        if self.bindResponseKeyIDList is not None:
            for i, keyID in enumerate(self.bindResponseKeyIDList):
                clickJS = 'document.getElementById("%d").click();' % i
                bindTuple = (keyID, clickJS)
                bindKeyTxt += ("\n" + html.bindKeySubSnippetJS % bindTuple)
        
        returnJS = ""
        if bindKeyTxt != "":
            returnJS = html.bindKeyJSTemplate % bindKeyTxt
        
        return returnJS

    def _getHTMLTxt(self):
        radioButton = ('<p>\n'
                       '<input type="radio" name="media_choice"'
                       'value="%(id)s" id="%(id)s" %(disabled)s />\n'
                       '<label for="%(id)s">.</label>\n'
                       '</p>\n'
                       )
        
        disabledTxt = ""
        if self._doPlayMedia():
            disabledTxt = "disabled"
        
        htmlTxt = ('<br /><br />%%s<br /><br />\n'
                   '<table class="center">\n'
                   '<tr>%s</tr>\n'
                   '<tr>%s</tr>\n'
                   '</table>\n'
                   )
        
        labelRow = ""
        buttonRow = ""
        for i in range(len(self.responseButtonList)):
            radioButtonTxt = radioButton % {'id': i, "disabled": disabledTxt}
            text = self.textDict[self.responseButtonList[i]]
            labelRow += "<td class='responses'>%s</td>" % text
            buttonRow += "<td class='responses'>%s</td>" % radioButtonTxt
        
        return htmlTxt % (labelRow,
                          buttonRow)
    
    def getValidation(self):
        template = ""
        
        return template
    
    def getOutput(self, form):
        
        try:
            value = super(MediaChoicePage, self).getOutput(form)
            if not self._doPlayMedia():
                value += ",0"

        except abstract_pages.KeyNotInFormError:  # User timed-out
            value = ",".join(['0'] * self.getNumOutputs()) + ",1"

        return value
    
    def getNumOutputs(self):
        return len(self.responseButtonList)
    
    def getHTML(self):
        '''
        Listeners hear two files and decide if they are the same or different
        '''
        pageTemplate = join(self.webSurvey.htmlDir, "axbTemplate.html")
        availableFunctions = getToggleButtonsJS(len(self.responseButtonList))
        
        # Generate the media buttons
        playBtnLabelRow = ''
        playBtnSnippet = ''
        template = "<td class='buttons'>%s</td>"
        for i in range(len(self.mediaList)):
            
            # Don't generate an audio button if the list is empty
            if len(self.mediaList[i]) == 0:
                continue
            
            audioLabel = self.textDict['play_button']
            mediaButtonHTML = audio.generateAudioButton(self.mediaList[i], i,
                                                        audioLabel,
                                                        self.pauseDuration,
                                                        False)
            if self.buttonLabelList is not None:
                label = self.textDict[self.buttonLabelList[i]]
                playBtnLabelRow += template % label
            playBtnSnippet += template % mediaButtonHTML
        
        # Add optional button labels
        playBtnSnippet = '<tr>%s</tr>' % playBtnSnippet
        if self.buttonLabelList is not None:
            playBtnLabelRow = '<tr>%s</tr>' % playBtnLabelRow
        
        playBtnSnippet = playBtnLabelRow + playBtnSnippet
        
        # Add optional speech transcripts
        if self.transcriptList is not None:
            transcriptList = [loader.loadTxtFile(join(self.txtDir,
                                                      transcript + ".txt"))
                              for transcript in self.transcriptList]
            transcriptList = ["<td>%s</td>" % "<br />".join(transcript)
                              for transcript in transcriptList]
                              
            transcriptTxt = "<tr>%s</tr>" % "".join(transcriptList)
            playBtnSnippet = playBtnSnippet + transcriptTxt
        
        playBtnSnippet = ('<table class="center">%s</table>') % playBtnSnippet
        
        runOnMinThresholdJS = "enable_checkboxes();"
        embedTxt = ""
        
        mediaNames = [mediaName for mediaSubList in self.mediaList
                      for mediaName in mediaSubList]
        if self._doPlayMedia():
            if self.audioOrVideo == "video":
                extList = self.webSurvey.videoExtList
            else:
                extList = self.webSurvey.audioExtList
            embedTxt += "\n\n" + audio.generateEmbed(self.wavDir,
                                                     list(set(mediaNames)),
                                                     extList,
                                                     self.audioOrVideo)
        
        embedTxt += "\n\n" + availableFunctions
        embedTxt += self._getKeyPressEmbed()
        
        description = self.textDict[self.instructionText]

        htmlText = description + self._getHTMLTxt()
        htmlText %= (playBtnSnippet + "<br />")
    
        return htmlText, pageTemplate, {'embed': embedTxt}
    
    def _doPlayMedia(self):
        mediaNames = [mediaName for mediaSubList in self.mediaList
                      for mediaName in mediaSubList]
        return len(mediaNames) > 0


def _buttonLabelCheck(audioListOfLists, buttonLabelList):

    txtKeyList = []

    if buttonLabelList is not None:
        if len(buttonLabelList) != len(audioListOfLists):
            raise UnbalancedListPair(audioListOfLists, buttonLabelList)
        txtKeyList += buttonLabelList
        
    return txtKeyList


def getToggleButtonsJS(numItems, idFormat=None):
    # Generate the javascript for disabling or enabling all of the
    # audio buttons
    enabledJS = 'document.getElementById("%s").disabled=false;\n'
    disabledJS = 'document.getElementById("%s").disabled=true;\n'
    
    enabledSnippet = ''
    disabledSnippet = ''
    for i in range(numItems):
        
        if idFormat is not None:
            idStr = idFormat % i
        else:
            idStr = str(i)
            
        enabledSnippet += (enabledJS % idStr)
        disabledSnippet += (disabledJS % idStr)
    
    jsCode = ('function enable_checkboxes() {\n'
              '%s'
              '}\n'
              'function disable_checkboxes() {\n'
              '%s'
              '}\n'
              ) % (enabledSnippet, disabledSnippet)
    
    return jsCode


class MediaSliderPage(abstract_pages.AbstractPage):
    
    pageName = "media_slider"
    
    def __init__(self, instructionText, audioOrVideo, minPlays, maxPlays,
                 mediaName, transcriptName, sliderMin, sliderMax,
                 sliderLabel=None, leftRangeLabel=None, rightRangeLabel=None,
                 *args, **kargs):
        super(MediaSliderPage, self).__init__(*args, **kargs)
        
        self.instructionText = instructionText
        self.audioOrVideo = audioOrVideo
        self.mediaName = mediaName
        self.transcriptName = transcriptName
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        self.sliderMin = sliderMin
        self.sliderMax = sliderMax
        self.leftRangeLabel = leftRangeLabel
        self.rightRangeLabel = rightRangeLabel
        
        self.playOnMinList = ['enable_checkboxes', ]
        
        if sliderLabel is None:
            sliderLabel = ""
        self.sliderLabel = sliderLabel
        
        self.txtDir = self.webSurvey.txtDir
        self.wavDir = self.webSurvey.wavDir
        
        self.submitProcessButtonFlag = True
        
        # Strings used in this page
        txtKeyList = [instructionText, ]
        
        if leftRangeLabel is not None:
            txtKeyList.append(leftRangeLabel)
        
        if rightRangeLabel is not None:
            txtKeyList.append(rightRangeLabel)
        
        txtKeyList.extend(abstract_pages.audioTextKeys)
        self.textDict.update(self.batchGetText(txtKeyList))
        
        self.numAudioButtons = 1
        self.processSubmitList = ["audioLoader.verifyAudioPlayed()", ]
        
    def _getHTMLTxt(self):
        
        htmlTxt = ('<br /><br />%%s<br /><br />\n'
                   '%s'
                   )
        
        if self.leftRangeLabel is not None:
            leftLabel = self.textDict[self.leftRangeLabel]
        else:
            leftLabel = ""
            
        if self.rightRangeLabel is not None:
            rightLabel = self.textDict[self.rightRangeLabel]
        else:
            rightLabel = ""
        
        sliderHTML = ('%(leftTxt)s<input type="range" name="media_slider" '
                      'min="%(min)s" max="%(max)s" id="%(id)s" disabled />'
                      '%(rightTxt)s<br />%(label)s <br />'
                      )
        sliderHTML %= {"min": str(self.sliderMin),
                       "max": str(self.sliderMax),
                       "leftTxt": leftLabel,
                       "rightTxt": rightLabel,
                       "id": "range0",
                       "label": str(self.sliderLabel)}
        
        return htmlTxt % sliderHTML
    
    def getValidation(self):
        template = ""
        
        return template
    
    def getOutput(self, form):
        
        value = form.getlist("media_slider")[0]
        value = utils.decodeUnicode(value)
            
        return value
    
    def getNumOutputs(self):
        return 1
    
    def getHTML(self):
        '''
        Listeners hear two files and decide if they are the same or different
        '''
        pageTemplate = join(self.webSurvey.htmlDir, "axbTemplate.html")
        availableFunctions = getToggleButtonsJS(1, "range%d")
        
        txtFN = join(self.txtDir, self.transcriptName + ".txt")
        sentenceList = loader.loadTxtFile(txtFN)
        transcriptTxt = "<br /><br />\n\n".join(sentenceList)

        audioLabel = self.textDict['play_button']
        playBtnSnippet = audio.generateAudioButton(self.mediaName, 0,
                                                   audioLabel,
                                                   0,
                                                   False)
        
        runOnMinThresholdJS = "enable_checkboxes();"
        embedTxt = ""
        
        mediaNames = [self.mediaName, ]
        
        if self.audioOrVideo == "audio":
            extList = self.webSurvey.audioExtList
        else:
            extList = self.webSurvey.videoExtList
        embedTxt += "\n\n" + audio.generateEmbed(self.wavDir,
                                                 list(set(mediaNames)),
                                                 extList,
                                                 self.audioOrVideo)
        embedTxt += "\n\n" + availableFunctions
        
        description = self.textDict[self.instructionText]

        htmlText = description + self._getHTMLTxt()
        htmlText %= (playBtnSnippet + "<br />" + transcriptTxt)
    
        return htmlText, pageTemplate, {'embed': embedTxt}


class MediaListPage(abstract_pages.AbstractPage):

    pageName = "media_list"

    def __init__(self, audioOrVideo, pauseDuration, minPlays, maxPlays,
                 mediaList, *args, **kargs):
        super(MediaListPage, self).__init__(*args, **kargs)
        self.audioOrVideo = audioOrVideo
        self.pauseDuration = pauseDuration
        self.mediaList = mediaList
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        
        self.autoSubmit = True
        
        assert(audioOrVideo in ["audio", "video"])
        
        self.wavDir = self.webSurvey.wavDir

        self.submitProcessButtonFlag = False

        # Strings used in this page
        txtKeyList = ["memory_instruct", "memory_a", "memory_b"]
        txtKeyList.extend(abstract_pages.audioTextKeys)
        self.textDict.update(self.batchGetText(txtKeyList))

        # Variables that all pages need to define
        
        # Although there are many files, there is just one button
        self.numAudioButtons = 1
        self.processSubmitList = ["audioLoader.verifyAudioPlayed()", ]
    
    def _getHTMLTxt(self):
        return "%s<br /><br />"
    
    def getValidation(self):
        return
    
    def getNumOutputs(self):
        return 0
    
    def getHTML(self):
    
        htmlText = self._getHTMLTxt()
        pageTemplate = join(self.webSurvey.htmlDir, "axbTemplate.html")
        
        audioLabel = self.textDict['play_button']
        htmlText %= audio.generateAudioButton(self.mediaList,
                                              0,
                                              audioLabel,
                                              self.pauseDuration,
                                              False, True) + "<br />"
        
        embedTxt = ""
        
        if self.audioOrVideo == "audio":
            extList = self.webSurvey.audioExtList
        else:
            extList = self.webSurvey.videoExtList
        embedTxt += "\n\n" + audio.generateEmbed(self.wavDir,
                                                 list(set(self.mediaList)),
                                                 extList,
                                                 self.audioOrVideo)
        
        return htmlText, pageTemplate, {'embed': embedTxt}
