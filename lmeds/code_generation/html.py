# -*- coding: utf-8 -*-
'''
Created on Mar 28, 2013

@author: timmahrt

Common HTML snippets
'''

import os

try:
    import Cookie as cookies
except ImportError:
    from http import cookies

from functools import partial

from lmeds.lmeds_io import loader

choice = """<input type="radio" name="radio">"""
img = """<img src="data/%s">"""
txtBox = """<input type="text" name="%s" value=""/>"""
radioButton = """<input type="radio" name="radio" value="%s">"""

pg2HTML = """
%%(explain)s<br /><br />
%(choiceA)s %%(consent)s\n
<br /><br />\n
%(choiceB)s %%(dissent)s
""" % {"choiceA": radioButton % "consent",
       "choiceB": radioButton % "dissent"
       }


formTemplate = """
<div id='audio_hook'></div>
<form class="submit" name="languageSurvey" method="POST">
%(html)s

<input TYPE="hidden" name="page" value="%(page)s">
<input TYPE="hidden" name="pageNumber" value="%(pageNumber)d">
<input TYPE="hidden" name="cookieTracker" value="%(cookieTracker)s">
<input TYPE="hidden" name="user_name" value="%(user_name)s">
<input TYPE="hidden" name="num_items" value="%(num_items)d">
<input TYPE="hidden" name="task_duration" id="task_duration" value="0">
%(audio_play_tracking_html)s
<br /><br />
%(submit_button_slot)s
</form>
"""

# This is more or less a HACK
# -- we needed to hide the submit button, but only in a single situation
# -- (it reappears after someone clicks another button--handled via javascript)
formTemplate2 = """
<div id='audio_hook'></div>
<form class="submit" name="languageSurvey" method="POST">
%(html)s

<div id="HiddenForm" style="DISPLAY: none">
<input TYPE="hidden" name="page" value="%(page)s">
<input TYPE="hidden" name="pageNumber" value="%(pageNumber)d">
<input TYPE="hidden" name="cookieTracker" value="%(cookieTracker)s">
<input TYPE="hidden" name="user_name" value="%(user_name)s">
<input TYPE="hidden" name="num_items" value="%(num_items)d">
<input TYPE="hidden" name="task_duration" id="task_duration" value="0">
%(audio_play_tracking_html)s
<br /><br />
%(submit_button_slot)s
</div>
</form>
"""

# From http://stackoverflow.com/questions/11807944/
# jquery-trigger-keypress-function-on-entire-document-but-not-inside-inputs-and-t
# Check for keypresses when the user isn't in a textfield
# eg

# Letters and some keys such as 'enter' are universal across browsers
# Otherwise, there are lots of imcompatibilities.  See
# http://unixpapa.com/js/key.html
bindKeyJSTemplate = ("""
$(document).on('keypress', function(e) {
    var tag = e.target.tagName.toLowerCase();
    if (tag != 'input' && tag != 'textarea') {
    %s
    }
});""")

bindKeySubSnippetJS = """if (e.which == %d) {%s}"""

bindToSubmitButtonJS = """
if (e.which == %d) {document.getElementById("submitButton").click();}
"""

submitButtonHTML = ('<input name="submitButton" id="submitButton" '
                    'type="button" value="%s">'
                    )


def keyboardletterToChar(letter):
    
    specialCodes = {"alt": 18,
                    "backspace": 8,
                    "capslock": 20,
                    "ctrl": 17,
                    "enter": 13,
                    "escape": 27,
                    "shift": 16,
                    "space": 32,
                    "tab": 9,
                    }
    
    # Exceptional cases
    lowerCaseLetter = letter.lower()
    if lowerCaseLetter in specialCodes.keys():
        retVal = specialCodes[lowerCaseLetter]
    
    # Normal case (ascii char)
    else:
        assert(len(letter) == 1)
        retVal = ord(str(letter))
    
    return retVal


def mapKeylist(keyIDList):
    
    tmpKeyIDList = []
    for keyID in keyIDList:
        keyID = keyboardletterToChar(keyID)
        tmpKeyIDList.append(keyID)
    
    return tmpKeyIDList


def getWidgetSubmit(widgetName):
    '''
    Associates all widgets with a provided name (%s) with the submit function
    '''
    widgetSubmit = ('// Set the radio buttons to submit the page on click\n'
                    'var radios = document.getElementsByName("%s");\n'
                    'for (var i = [0]; i < radios.length; i++) {\n'
                    'radios[i].onclick=processSubmit;\n'
                    '}\n\n')
    widgetSubmit %= widgetName
    
    return widgetSubmit


def getTimeoutSubmit(timeS):
    '''Associates a timeout with the submit function'''
    timeoutSubmit = "setTimeout(processSubmit, %d);" % int(float(timeS) * 1000)
    return timeoutSubmit


def constructSubmitAssociation(tupleList):
    returnStr = ""
    assocDict = {'widget': getWidgetSubmit,
                 'timeout': getTimeoutSubmit}
    for task, arg in tupleList:
        returnStr += assocDict[task](arg) + "\n"
    
    return returnStr


# Associates a submit button with
runOnPageLoad = """
// The code that runs when the page is finished loading
window.onload=function() {
timer = new Timer()

%s
}

"""

audioPlayTrackingTemplate = ('<input TYPE="hidden" '
                             'name="audioFilePlays%(id)d" '
                             'id="audioFilePlays%(id)d" value="0" />\n'
                             )


def createChoice(textList, i, checkboxFlag=False):
    
    widgetTemplate = '<input type="radio" name="%s" id="%s" value="%s">'
    if checkboxFlag:
        widgetTemplate = '<input type="checkbox" name="%s" id="%s" value="%s">'
        
    choiceList = []
    for text in textList:
        newRadioButton = widgetTemplate % (str(i), str(i), text)
        choiceList.append("%s %s" % (text, newRadioButton))
    
    txtSeparator = "&nbsp;" * 4
    
    return "%s" % txtSeparator.join(choiceList), i + 1


def createChoicebox(textList, i):
    
    widgetTemplate = """<option value="%s">%s</option>"""
    
    choiceList = []
    for j, text in enumerate(textList):
        newChoice = widgetTemplate % (str(j), text)
        choiceList.append(newChoice)
        
    returnTxt = """<select name="%s" id="%s">%%s</select>""" % (str(i), str(i))
    returnTxt %= "\n".join(choiceList)
    
    return returnTxt, i + 1


def createSlidingScale(textList, i):
    leftVal, rightVal, leftText, rightText = textList
    widgetTemplate = ('<input type="range" name="%s" id="%s" value=""'
                      'min="%s" max="%s">')
    widgetTemplate %= (str(i), str(i), leftVal, rightVal)
    
    return leftText + widgetTemplate + rightText, i + 1
    

def createTextbox(i):
    tmpTxtBox = """<input type="text" name="%s" id="%s" value=""/>"""
    return tmpTxtBox % (str(i), str(i)), i + 1


def createTextfield(i, argList):
    width = argList[0]  # Units in number of characters
    numRows = argList[1]
    
    txtFieldStr = '<textarea name="%s" id="%s" rows="%s" cols="%s"></textarea>'
    txtFieldStr %= (str(i), str(i), numRows, width)
    
    return txtFieldStr, i + 1

    
def createWidget(widgetType, argList, i):

    elementDictionary = {"Choice": createChoice,
                         "Item_List": partial(createChoice, checkboxFlag=True),
                         "Choicebox": createChoicebox,
                         "Sliding_Scale": createSlidingScale,
                         }
    
    if widgetType == "Textbox":
        widgetHTML, i = createTextbox(i)
    elif widgetType == "Multiline_Textbox":
        widgetHTML, i = createTextfield(i, argList)
    else:
        widgetHTML, i = elementDictionary[widgetType](argList, i)
        
    return widgetHTML, i


def getLoadingNotification(loadingProgressTxt):
    loadingText = "- %s - " % loadingProgressTxt
    progressBarTemplate = """
    <div id="loading_status_indicator" class="centered_splash">
    <div class="centered_splash_inner">
    %s
    <dl class="progress">
        <dt>Completed:</dt>
        <dd id="loading_percent_done" class="done" style="width:0%%">
            <a href="/"></a>
        </dd>
    
        <dt >Left:</dt>
        <dd id="loading_percent_left" class="left" style="width:100%%">
            <a href="/"></a>
        </dd>
    </dl>

    </div>
    </div>
    """
    
    return progressBarTemplate % loadingText
    

def getProgressBar(progressTxt):
    progressBarText = "- %s - <br />" % progressTxt
    
    progressBarTemplate = progressBarText + """
    <dl class="progress">
        <dt>Completed:</dt>
        <dd class="done" style="width:%(percentComplete)s%%%%">
            <a href="/"></a>
        </dd>
    
        <dt >Left:</dt>
        <dd class="left" style="width:%(percentUnfinished)s%%%%">
            <a href="/"></a>
        </dd>
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
        cookie = cookies.SimpleCookie(os.environ["HTTP_COOKIE"])
        oldPageNum = int(cookie["lastPage"].value)
    except(cookies.CookieError, KeyError):
        if pageNum != 0:
            print(("\n\nERROR: Page number is %d according to index.cgi "
                   "but no cookies found") % pageNum)
            exit(0)
    else:
        if pageNum <= oldPageNum and pageNum != 0:
            print("\n\nERROR: Back button or refresh detected",
                  pageNum, oldPageNum)
            exit(0)
    
#    # Set expiration five minutes from now
#    expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)
    cookie = cookies.SimpleCookie()
    cookie["lastPage"] = pageNum
    
    return cookie, oldPageNum, pageNum


def printCGIHeader(pageNum, disableRefreshFlag):
    '''
    Prints the html header
    
    This header must get printed before the website will render
    new text as html
    
    A double newline '\n\n' indicates the end of the header.
    '''
    print('Content-Type: text/html')
    
    if disableRefreshFlag:
        print("Pragma-directive: no-cache\n"
              "Cache-directive: no-cache\n"
              "Cache-Control: no-cache, no-store, must-revalidate\n"
              "Pragma: no-cache\n"
              "Expires: 0\n")
        cookieStr = validateAndUpdateCookie(pageNum)[0]
        print(cookieStr)
    print("\n\n")


def makeNoWrap(htmlTxt):
    return '<div id="noTextWrapArea">\n\n%s\n\n</div>' % htmlTxt


def makeWrap(htmlTxt):
    return '<div id="textWrapArea">\n\n%s\n\n</div>' % htmlTxt


processSubmitHTML = """
// The code that gets run when the page is submitted
function processSubmit()
{
    document.getElementById("task_duration").value = document.myTimer.calcDuration();
    var returnValue = true;
    
    %s
    
    if (returnValue == true) {
        document.languageSurvey.submit()
    }
    return returnValue;
}\n
"""

if __name__ == "__main__":
    loader.initTextDict("../english.txt")
