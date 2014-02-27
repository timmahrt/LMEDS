# -*- coding: utf-8 -*-
'''
Created on Mar 28, 2013

@author: timmahrt
'''

import os
from os.path import join
import Cookie

import loader

import constants

choice = """<input type="radio" name="radio">"""
img = """<img src="data/%s">"""
txtBox = """<input type="text" name="%s" value=""/>"""
radioButton = """<input type="radio" name="radio" value="%s">"""

pg2HTML = """
%%(explain)s<br /><br />
%(choiceA)s %%(consent)s\n
<br /><br />\n
%(choiceB)s %%(dissent)s
""" % {"choiceA":radioButton % "consent",
       "choiceB":radioButton % "dissent"
       }


formTemplate = """
<form class="submit" name="languageSurvey" method="POST" action="%(source_cgi_fn)s" onsubmit="return processSubmit();">
%(html)s

<input TYPE="hidden" name="page" value="%(page)s"> 
<input TYPE="hidden" name="pageNumber" value="%(pageNumber)d"> 
<input TYPE="hidden" name="cookieTracker" value="%(cookieTracker)s"> 
<input TYPE="hidden" name="user_name" value="%(user_name)s"> 
<input TYPE="hidden" name="num_items" value="%(num_items)d">
<input TYPE="hidden" name="task_duration" id="task_duration" value="0">
<input TYPE="hidden" name="audioFilePlays0" id="audioFilePlays0" value="0" />
<input TYPE="hidden" name="audioFilePlays1" id="audioFilePlays1" value="0" />
<br /><br />
<input id="submit" TYPE="submit" value="%(submit_button_text)s">
</form>
"""

# This is more or less a HACK 
# -- we needed to hide the submit button, but only in a single situation
# -- (it reappears after someone clicks another button--handled via javascript)
formTemplate2 = """
<form class="submit" name="languageSurvey" method="POST" action="%(source_cgi_fn)s" onsubmit="return processSubmit();">
%(html)s

<div id="HiddenForm" style="DISPLAY: none">
<input TYPE="hidden" name="page" value="%(page)s"> 
<input TYPE="hidden" name="pageNumber" value="%(pageNumber)d"> 
<input TYPE="hidden" name="cookieTracker" value="%(cookieTracker)s"> 
<input TYPE="hidden" name="user_name" value="%(user_name)s"> 
<input TYPE="hidden" name="num_items" value="%(num_items)d">
<input TYPE="hidden" name="task_duration" id="task_duration" value="0">
<input TYPE="hidden" name="audioFilePlays0" id="audioFilePlays0" value="0" />
<input TYPE="hidden" name="audioFilePlays1" id="audioFilePlays1" value="0" />
<br /><br />
<input id="submit" TYPE="submit" value="%(submit_button_text)s">
</div>
</form>
"""

taskDurationCode = """
<script type="text/javascript">

var start = new Date().getTime();

function calcDuration() {
    var time = new Date().getTime() - start;

    var seconds = Math.floor(time / 100) / 10;
    var minutes = Math.floor(seconds / 60);
    seconds = seconds - (minutes * 60);
    if(Math.round(seconds) == seconds) { 
        seconds += '.0'; 
    }
    var param1 = minutes.toString();
    var param2 = Number(seconds).toFixed(1);
    document.getElementById("task_duration").value = param1 + ":" + param2;
}
</script>
"""
def getProgressBar():
    progressBarText = "- %s - <br />" % loader.getText("progress")
    
    progressBarTemplate = progressBarText + """
    <dl class="progress">
        <dt>Completed:</dt>
        <dd class="done" style="width:%(percentComplete)s%%%%"><a href="/"></a></dd>
    
        <dt >Left:</dt>
        <dd class="left" style="width:%(percentUnfinished)s%%%%"><a href="/"></a></dd>
    </dl>
    """
    
    return progressBarTemplate


def validateAndUpdateCookie(pageNum):
    '''
    Tracks the progress of pages.  If a page is reloaded, terminate execution.
    
    In order to implement this, the pageNum must always increase by an
    arbitrary amount with each new page.  If the pageNum is less than or equal
    to what it was before, this indicates the reloading of an older page.
    
    Terminating the test prevents users from hitting /back/ and then /forward/
    to wipe page-variables like num-of-times-audio-file-played.
    '''
    oldPageNum = -1
    try:
        cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
        oldPageNum = int(cookie["lastPage"].value)
    except(Cookie.CookieError, KeyError):
        if pageNum != 0:
            print "\n\nERROR: Page number is %d according to index.cgi but no cookies found" % pageNum
            exit(0)
    else:
        if pageNum <= oldPageNum and pageNum != 0:
            print "\n\nERROR: Back button or refresh detected", pageNum, oldPageNum
            exit(0)
    
#    # Set expiration five minutes from now
#    expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
    cookie = Cookie.SimpleCookie()
    cookie["lastPage"] = pageNum
    
    return cookie, oldPageNum, pageNum


def printCGIHeader(pageNum, disableRefreshFlag):
    '''
    This header must get printed before the website will render new text as html
    
    A double newline '\n\n' indicates the end of the header.
    '''
    print 'Content-Type: text/html'
    
    if disableRefreshFlag:
        print "Pragma-directive: no-cache"
        print "Cache-directive: no-cache"
        print "Cache-Control: no-cache, no-store, must-revalidate"
        print "Pragma: no-cache"
        print "Expires: 0"
        cookieStr= validateAndUpdateCookie(pageNum)[0]
        print cookieStr
    print "\n\n"


def firstPageHTML():
    txtBox = """<input type="text" name="%s" value=""/>"""
    productNote = """%s <br /> 
<b><i>%s</i></b><br /><br />\n\n""" % (loader.getText('experiment header'),
                                       constants.softwareName)
    
    title = """<div><p id="title">%s</p></div>\n\n""" % loader.getText('title')
    
    backButtonWarning = loader.getText('back button warning')
    pg0HTML = loader.getText('user name text') + "<br /><br />"
    pg0HTML += (txtBox % 'user_name_init') + "<br /><br />" + backButtonWarning
    
    unsupportedWarning = '''<div id="unsupported_warning"><br /><br /><font color="blue"><b>
    The web browser you are using does not support features required by LMEDS.  
    Please update your software
    or download a modern modern such as Chrome or Firefox.</b></font></div>'''
     
    return productNote + title + pg0HTML + unsupportedWarning


def firstPageErrorHTML():
    
    pg0HTML = firstPageHTML()
    pg0HTML = pg0HTML


    pg0HTML += "<br />" + loader.getText('error user name exists')

    return pg0HTML


def instructionPageHTML():
    
    instructionText = """Instruction Page<br/><br/>In this study, you will...
    <br/><br/>Each sound file is playable twice.  After listening to the audio, 
    make your judgements and move on to the next page."""
    
    return instructionText


def breakPageHTML():

    return loader.getText('section finished')

    
def consentPageHTML():
    
    consentText = open(join(constants.htmlSnippetsDir, "consent.html"), "r").read()
    consentText %= (loader.getText("title"),
                    loader.getText("consent title"),
                    loader.getText("consent text"))
    
    consentText += "\n\n<hr /><br /><br />%s" % loader.getText("consent query")

#    radioButton = """<input type="radio" name="radio" value="%s">"""

    consentButton = radioButton % "consent"
    dissentButton = radioButton % "dissent"

    consentChoice = '%s %s\n<br /><br />%s %s' % (consentButton, 
                                                  loader.getText("consent"),
                                                  dissentButton,
                                                  loader.getText("dissent"))

    consentHTML = consentText + "<br /><br />" + consentChoice

    return consentHTML


def consentEndPageHTML():
    
    consentErrorHTML = ""
    
    return consentErrorHTML


def axbPageHTML():
    
    radioButton = '<p><input type="radio" name="axb" value="%(id)s" id="%(id)s" /> <label for="%(id)s">.</label></p>'
    
    html = """%s<br /><br /><br />
%s<br /> <br />
%%s<br /> <br />
<table class="center">
<tr><td>%s</td><td>%s</td></tr>
<tr><td>%%s</td><td>%%s</td></tr>
<tr><td>%s</td><td>%s</td></tr>
</table>"""
    html %= (loader.getText("axb query"),
             loader.getText("x"),
             loader.getText("a"),
             loader.getText("b"),
             radioButton % {'id':'0'}, 
             radioButton % {'id':'1'})
    
#     html %= ('<p><input type="radio" value="A" id="A" name="gender" /> <label for="A">Male</label></p>',
#             '<p><input type="radio" value="B" id="B" name="gender" /> <label for="B ">Female</label></p>')
    
    return html


def audioDecisionPageHTML():
    
    radioButton = '<p><input type="radio" name="abn" value="%(id)s" id="%(id)s" /> <label for="%(id)s">.</label></p>'
    
    html = """
    %%s
<table class="center">
<tr><td>%%s</td><td>%%s</td><td>%%s</td></tr>
<tr><td>%s</td><td>%s</td><td>%s</td></tr>
</table>""" 
    
    return html % (radioButton % {'id':'0'},
                   radioButton % {'id':'1'},
                   radioButton % {'id':'2'})

def abPageHTML():
    
    radioButton = '<p><input type="radio" name="ab" value="%(id)s" id="%(id)s" /> <label for="%(id)s">.</label></p>'
    
    html = """Write statement about how the user should select (A) or (B).<br /><br />
<table class="center">
<tr><td>A</td><td>B</td></tr>
<tr><td>%%s</td><td>%%s</td></tr>
<tr><td>%s</td><td>%s</td></tr>
</table>"""
    html %= (radioButton % {'id':'0'}, 
             radioButton % {'id':'1'})
    
    return html    


def constructTable(wordList, doBreaks, doProminence, offsetNum):
    

    breakSign = "|" 
    breakHTML = '<p><input type="checkbox" name="b" value="%(num)d" id="%(num)d"/> <label for="%(num)d">.</label></p>\n'
    prominenceHTML = '<p><input type="checkbox" name="p" value="%(num)d" id="%(num)d"/> <label for="%(num)d">.</label></p>\n'
    
    
    # Set the prominence marks
    row1List = wordList
    bCheckboxList = []
    pCheckboxList = [prominenceHTML % {'num':i+offsetNum} for i, word in enumerate(wordList)]
    
    # Set the breaks
    if doBreaks:
        
        row1ListCopy = []
        pCheckboxListCopy = []
        
#        row1List = [breakSign,]
        bCheckboxList = []
        for i, wordTuple in enumerate( zip(row1List,pCheckboxList) ):
            word, pCheckbox = wordTuple
            
            row1ListCopy.append(word)
            row1ListCopy.append(breakSign)
            
            bCheckboxList.append("")
            bCheckboxList.append(breakHTML % {'num':i})
            
            pCheckboxListCopy.append(pCheckbox)
            pCheckboxListCopy.append("")
        
        row1List = row1ListCopy[:-1]
        pCheckboxList = pCheckboxListCopy[:-1]
        bCheckboxList = bCheckboxList[:-1]
        
    textRow = "</td><td>".join(row1List)

    
    rowHTML = "<tr><td>%s</td></tr>"
    
    allRows = ""
    allRows += rowHTML % textRow
    
    if doBreaks:
        bCheckboxRow = "</td><td>".join(bCheckboxList)
        allRows += rowHTML % bCheckboxRow 
    
    if doProminence:
        pCheckboxRow = "</td><td>".join(pCheckboxList)
        allRows += rowHTML % pCheckboxRow   
    
    html = '<table class="center">%s</table>' % allRows

    return html


def makeTogglableWord(testType, word, idNum):
    
    html = """
<label for="%(idNum)d">
                <input type="checkbox" name="%(testType)s" id="%(idNum)d" value="%(idNum)d"/>
                %(word)s
</label>\n\n
"""

    return html % {"testType":testType,"word":word, "idNum":idNum}


def getTogglableWordEmbed(numWords):
    
    javascript = """
<script type="text/javascript" src="jquery.min.js"></script>
    
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
            $("#"+x).closest("label").css({ borderRight: "3px solid #000000"});
            $("#"+x).closest("label").css({ paddingRight: "0px"});
            }
        }
    }
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
    $(this).closest("label").css({ borderRight: this.checked ? "3px solid #000000":"0px solid #FFFFFF"});
    $(this).closest("label").css({ paddingRight: this.checked ? "0px":"3px"});
    }
    else
    {
    $(this).closest("label").css({ color: this.checked ? "red":"black"});
    }
  });
});
</script>"""

    return javascript % {"numWords":numWords}


def getProminenceOrBoundaryWordEmbed(isProminence):
    
    boundaryEmbed = """
    $(this).closest("label").css({ borderRight: this.checked ? "3px solid #000000":"0px solid #FFFFFF"});
    $(this).closest("label").css({ paddingRight: this.checked ? "0px":"3px"});
    """
    
    prominenceEmbed = """
    $(this).closest("label").css({ color: this.checked ? "red":"black"});
    """
    
    javascript = """
<script type="text/javascript" src="jquery.min.js"></script>

    
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


def getProcessSubmitHTML(pageType):
    '''
    processSubmit() is a javascript function whose job is only to launch
    other javascript functions.  These functions need to be registered with
    a page in order to receive that functionality.
    '''
    
    baseHTML = """
<script  type="text/javascript">
function processSubmit()
{
calcDuration();
var returnValue = true;

%s

return returnValue;    
}
</script>
"""
    
    funcList = []
    # Ensure the subject has listened to all audio files
    if pageType in ['axb', 'prominence', 'boundary', 'boundaryAndProminence',
                    'oldProminence', 'oldBoundary', 'abn']:
        funcList.append("verifyAudioPlayed")
        
    # Ensure all required forms have been filled out
    if pageType in ['login', 'login_bad_user_name', 'consent', 'axb', 'ab', 'abn']:
        funcList.append("validateForm")
    
    htmlList = []
    for func in funcList:
        htmlList.append("returnValue = returnValue && %s();" % func)
    
    htmlTxt = "\n".join(htmlList)
    
    return baseHTML % htmlTxt


if __name__ == "__main__":
    loader.initTextDict("../english.txt")
    print firstPageErrorHTML()

