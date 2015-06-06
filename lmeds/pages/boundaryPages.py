'''
Created on Mar 1, 2014

@author: tmahrt


'''

from os.path import join 

from lmeds import html
from lmeds import audio
from lmeds import constants
from lmeds import loader

from lmeds.pages import abstractPages


def _doBreaksOrProminence(testType, wordIDNum, audioNum, name, textName, sentenceList, presentAudioFlag, token):
    '''
    This is a helper function.  It does not construct a full page.
    
    Can be used to prepare text for prominence OR boundary annotation
    (or both if called twice and aggregated).
    '''
    
    htmlTxt = ""
    
    instrMsg = ("%s<br /><br />\n\n" % loader.getText(textName))
    htmlTxt += html.makeWrap(instrMsg)
    
    if presentAudioFlag.lower() == 'true':
        htmlTxt += audio.generateAudioButton(name, audioNum, False) + "<br /><br />\n\n"
    else:
        htmlTxt += "<br /><br />\n\n"
    
    sentenceListTxtList = []
    for sentence in sentenceList:
        if '<' in sentence:
            sentenceListTxtList.append(sentence)
        else:
            wordList = sentence.split(" ")
            tmpHTMLTxt = ""
            for word in wordList:
                # If a word is an HTML tag, it isn't togglable.  Otherwise, it is
                tmpHTMLTxt += _makeTogglableWord(testType, word, wordIDNum, token)
                wordIDNum += 1 

            sentenceListTxtList.append(tmpHTMLTxt)
        
#             # New sentence, new line
#             if len(sentenceListTxtList) == 0:
#                 sentenceListTxtList.append(tmpHTMLTxt)
#             else:
#                 sentenceListTxtList[-1] += tmpHTMLTxt
    
    newTxt = "<br /><br />\n\n".join(sentenceListTxtList)
#     htmlTxt += "<br /><br />\n\n"
            
    htmlTxt += newTxt
            
    return htmlTxt, wordIDNum


def _getProminenceOrBoundaryWordEmbed(isProminence):
    
    boundaryEmbed = """
    $(this).closest("label").css({ borderRight: this.checked ? "3px solid #000000":"0px solid #FFFFFF"});
    $(this).closest("label").css({ paddingRight: this.checked ? "0px":"3px"});
    """
    
    prominenceEmbed = """
    $(this).closest("label").css({ color: this.checked ? "red":"black"});
    """
    
    javascript = """
<script type="text/javascript" src="jquery-1.11.0.min.js"></script>

    
<style type="text/css">
           /* Style the label so it looks like a button */
           label {
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


def _makeTogglableWord(testType, word, idNum, boundaryToken):
    
    tokenTxt = ""
    if boundaryToken != None:
        tokenTxt = """<span class="hidden">%s</span>""" % boundaryToken
    
    htmlTxt = """
<label for="%(idNum)d">
                <input type="checkbox" name="%(testType)s" id="%(idNum)d" value="%(idNum)d"/>
                %(word)s""" + tokenTxt + """\n</label>\n\n"""

    return htmlTxt % {"testType":testType,"word":word, "idNum":idNum}


def _getTogglableWordEmbed(numWords, boundaryMarking):
    

    boundaryMarkingCode_showHide = """
            $("#"+x).closest("label").css({ borderRight: "3px solid #000000"});
            $("#"+x).closest("label").css({ paddingRight: "0px"});
    """
    
    boundaryMarkingCode_toggle = """    
    $(this).closest("label").css({ borderRight: this.checked ? "3px solid #000000":"0px solid #FFFFFF"});
    $(this).closest("label").css({ paddingRight: this.checked ? "0px":"3px"});"""
    if boundaryMarking != None:
        boundaryMarkingCode_toggle = """
        $(this).next("span").css({ visibility: this.checked ? "visible":"hidden"});
        """
        boundaryMarkingCode_showHide = """
        $("#"+x).next("span").css({ visibility: "visible"});
        """
    
    

    
    javascript = """
<script type="text/javascript" src="jquery-1.11.0.min.js"></script>
    
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
           label {
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

    return javascript % {"numWords":numWords, "boundaryMarkingCode_toggle":boundaryMarkingCode_toggle,
                         "boundaryMarkingCode_showHide":boundaryMarkingCode_showHide}


class BoundaryOrProminenceAbstractPage(abstractPages.AbstractPage):
    
    def __init__(self, name, transcriptName, minPlays, maxPlays, instructions=None, presentAudio="true", boundaryToken=None, doProminence=True, *args, **kargs):
        
        super(BoundaryOrProminenceAbstractPage, self).__init__(*args, **kargs)
        
        self.name = name
        self.transcriptName = transcriptName
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        self.instructions = instructions
        self.presentAudio = presentAudio
        self.boundaryToken = boundaryToken
        self.doProminence = doProminence
        
        self.txtDir = self.webSurvey.txtDir
        self.wavDir = self.webSurvey.wavDir
    
        # Variables that all pages need to define
        if presentAudio == "true":
            self.numAudioButtons = 1
        else:
            self.numAudioButtons = 0
        self.processSubmitList = ["verifyAudioPlayed",]
        
    
    def getValidation(self):
        template = ""
        
        return template
        
        
    def getNumOutputs(self):
        # One binary label for every word
        return loader.getNumWords(join(self.txtDir, self.transcriptName+".txt"))
    
    
    def getHTML(self):
        '''
        Returns html for a page where users mark either breaks or prominence
        
        
        '''
        pageTemplate = join(constants.htmlDir, "wavTemplate.html")
        
        txtFN = join(self.txtDir, self.transcriptName+".txt")
        
        sentenceList = loader.loadTxt(txtFN)
        
        textName = [self.sequenceName, "instructions short"]
        testType = self.sequenceName
        
        if self.instructions != None:
            textName.insert(1, self.instructions)
        
        # Construct the HTML here
        htmlTxt = _doBreaksOrProminence(testType, 0, 0, self.name, " ".join(textName), sentenceList, self.presentAudio, self.boundaryToken)[0]
    
        if self.presentAudio:
            embedTxt = audio.getPlayAudioJavaScript(True, 1, [self.maxPlays,], self.minPlays)
            embedTxt += "\n\n" + audio.generateEmbed(self.wavDir, [self.name,])
        else:
            embedTxt = ""
        embedTxt += "\n\n" + _getProminenceOrBoundaryWordEmbed(self.doProminence)
        
        htmlTxt = html.makeNoWrap(htmlTxt)
        
        return htmlTxt, pageTemplate, {'embed':embedTxt}


class BoundaryPage(BoundaryOrProminenceAbstractPage):
    
    sequenceName = "boundary"
    
    def __init__(self, *args, **kargs):
        kargs["doProminence"] = False
        super(BoundaryPage, self).__init__(*args, **kargs)
    
    
class ProminencePage(BoundaryOrProminenceAbstractPage):
    
    sequenceName = "prominence"
    
    def __init__(self, *args, **kargs):
        kargs["doProminence"] = True
        super(ProminencePage, self).__init__(*args, **kargs)
        

class BoundaryAndProminencePage(abstractPages.AbstractPage):

    sequenceName = 'boundary_and_prominence'

    def __init__(self, name, transcriptName, minPlays, maxPlays, instructions=None, presentAudio="true", boundaryToken=None, *args, **kargs):
        
        super(BoundaryAndProminencePage, self).__init__(*args, **kargs)
        
        # Sanity force
        if presentAudio.lower() == "false":
            minPlays = "0"
        
        self.name = name
        self.transcriptName = transcriptName
        self.minPlays = minPlays
        self.maxPlays = maxPlays
        self.instructions = instructions
        self.presentAudio = presentAudio
        self.boundaryToken = boundaryToken
        
        self.txtDir = self.webSurvey.txtDir
        self.wavDir = self.webSurvey.wavDir
        
        # Variables that all pages need to define
        if presentAudio == "true":
            self.numAudioButtons = 2 # Only show one at a time, plays the same audio
        else:
            self.numAudioButtons = 0
        self.processSubmitList = ["verifyAudioPlayed",]
        
    
    def getValidation(self):
        template = ""
        
        return template
    
    
    def getNumOutputs(self):
        # 1 binary boundary mark and 1 prominence mark for every word
        numWords = loader.getNumWords(join(self.txtDir, self.transcriptName+".txt"))
        return numWords * 2 
        
        
    def getHTML(self):
        '''
        Returns html for a page where users mark both breaks and prominence
        
        Subjects first mark up the boundaries.  They are then shown the same utterance
        with their original markings still present.  They are then asked to mark
        boundaries.
        
        'focus' - either 'meaning' or 'acoustics' -- used to print the correct
            instructions
        '''
        
        pageTemplate = join(constants.htmlDir, "wavTemplate.html")
        
        txtFN = join(self.txtDir, self.transcriptName+".txt")
        
        sentenceList = loader.loadTxt(txtFN)
        
        # Construct the HTML here
        # There are two passes of the utterance.  The first is for boundaries.
        # After
        wordIDNum = 0
        htmlTxt = '<div id="ShownDiv" style="DISPLAY: block">'
    
        # HTML boundaries
        instructionsText = ["boundary", "instructions short"]
        if self.instructions != None:
            instructionsText.insert(1, self.instructions)
        tmpHTMLTxt, numWords = _doBreaksOrProminence(self.sequenceName, wordIDNum, 0,self.name, 
                                                     " ".join(instructionsText), 
                                                     sentenceList,
                                                     self.presentAudio, 
                                                     self.boundaryToken)
        htmlTxt += "<div>%s</div>" % tmpHTMLTxt
    
        # HTML from transitioning from the boundary portion of text to the prominence portion
        htmlTxt += '<br /><br /><input type="button" value="%s" onclick="ShowHide()"></button>' % loader.getText('continue button')
        htmlTxt += '</div>\n\n<div id="HiddenDiv" style="DISPLAY: none">\n\n'
        
        # HTML prominence
        instructionsText = ["prominence", "post boundary instructions short"]
        if self.instructions != None:
            instructionsText.insert(1, self.instructions)
        htmlTxt += _doBreaksOrProminence(self.sequenceName, numWords, 1, self.name, 
                                         " ".join(instructionsText), 
                                         sentenceList,
                                         self.presentAudio,
                                         self.boundaryToken)[0]
        htmlTxt += "</div>"
                    
        # Closing off the div for the prominence section
        #htmlTxt += '</div>' # The last div will be closed off by 'formTemplate2'
                    
        # Add the javascript and style sheets here
        if self.presentAudio:
            embedTxt = audio.getPlayAudioJavaScript(True, 2, [self.maxPlays, self.maxPlays,], self.minPlays)
            embedTxt += "\n\n" + audio.generateEmbed(self.wavDir, [self.name,])
        else:
            embedTxt = ""

        embedTxt += "\n\n" + _getTogglableWordEmbed(numWords, self.boundaryToken)
        
        htmlTxt = html.makeNoWrap(htmlTxt)
        
        return htmlTxt, pageTemplate, {'embed':embedTxt}
    
    
    
    
