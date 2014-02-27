#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import constants

import wave
import contextlib
import loader

embedTemplate = """
<audio id="%s" preload="auto"> 
<source src="%s" type="audio/ogg">
<source src="%s" type="audio/mpeg">
</audio>
"""

#embedTemplate = """
#<embed autostart=false width=1 height=1 id="%s" src="%s"
#enablejavascript="true" hidden="true"></embed>
#"""

buttonTemplate = """
<input type="button" id="button%%d" value="%(button_label)s" onClick="EvalSound('%%s',this, true, '%%d')">
"""
#<input type="button" value="Play Sound" onClick="EvalSound('%s',this, true, 2)">
#<input type="button" value="Play Sound" onClick="document.getElementById('%s').play()">

buttonTemplateExample = """
<input type="button" id="button%%d" value="%(button_label)s" onClick="EvalSound('%%s',this, false, '%%d')">
"""


playAudioFileJS = '''
    <script>
var silenceFlag = %(silenceFlag)s;
var numSoundFiles = %(numSoundFiles)d;
var countDict = {
%(countDictTxt)s
};
var maxDict = {
%(maxDictTxt)s
};
function EvalSound(soundobj, button, silenceFlag, id) {
  audioFile = document.getElementById(soundobj);
  audioFile.currentTime = 0;
  audioFile.addEventListener('ended', enable);
  audioFile.play();

    for (var i=0;i<numSoundFiles;i++)
    { 
    document.getElementById("button"+i.toString()).disabled=true;
    }

    document.getElementById('audioFilePlays'+id.toString()).value = parseInt(document.getElementById('audioFilePlays'+id.toString()).value) + 1;

  countDict[id] = countDict[id] + 1;
  
  return true;
}
function enable() {
        for (var i=0; i<numSoundFiles;i++)
        {
        if (silenceFlag == false || maxDict[i] < 0 || countDict[i] < maxDict[i])
            {
            document.getElementById("button"+i.toString()).disabled=false;
            }
        }
    }
function verifyAudioPlayed() {
    var doAlert = false;
    var returnValue = true;
    for (var i=0; i<numSoundFiles;i++)
    {
    if (countDict[i] < %(minNumPlays)d)
        {
        doAlert = true;
        }
    }
        
    if (doAlert == true) {
        alert("%(minNumPlaysErrorMsg)s");
        returnValue = false;
    }

    return returnValue;
}
function verifyFirstAudioPlayed() {
    returnValue = true;
    if(countDict["0"] < %(minNumPlays)d)
    {
    alert("%(minNumPlaysErrorMsg)s");
    returnValue = false;
    }
    return returnValue;
}
    </script>
'''

oldPlayAudioFileJS = '''
    <script>
var countDict = {
%s
}
function EvalSound(soundobj, button, silence, max, id) {
  audioFile = document.getElementById(soundobj);
  
  audioFile.play();
  if(silence==true && countDict[id]>=max-1)
      {
      button.disabled=true;
      
     }
  else
  {
  button.disabled=true;
  setTimeout(function(){button.disabled=false;}, (audioFile.duration+0.5)*1000);
  }
  countDict[id] = countDict[id] + 1;
}
function enable() {
        button.disabled=false;
    }
    </script>
'''

def getPlayAudioJavaScript(doSilence, numItems, maxList, minNumPlays):

    maxList = [int(val) for val in maxList]
    minNumPlays = int(minNumPlays)

    if doSilence:
        silenceFlag = 'true'
    else:
        silenceFlag = 'false'
    
    maxDictionaryTextList = []
    for i, maxV in enumerate(maxList):
        maxDictionaryTextList.append('"%s":%d,' % (i, maxV))
    maxDictionaryText = "\n".join(maxDictionaryTextList)
    
    dictionaryTextList = []
    for i in xrange(numItems):
        dictionaryTextList.append('"%s":0,' % (i))
    countDictionaryText = "\n".join(dictionaryTextList)
    
    # Get error message and make sure it is formatted correctly
    if minNumPlays < maxList[0]:
        errorKey = "error must play audio at least"
    else:
        errorKey = "error must play audio"
        
    errorMsg = loader.getText(errorKey)
    if "%d" not in errorMsg:
        badFormattedText = "Please add a '%d', for the minimum number of required audio plays, in the text file"
        raise loader.BadlyFormattedTextError(badFormattedText, errorKey)
    
    
    minNumPlaysErrorMsg =  errorMsg % int(minNumPlays)
    
    jsCode = playAudioFileJS % {"silenceFlag":silenceFlag, 
                                "numSoundFiles":numItems, 
                                "countDictTxt":countDictionaryText, 
                                "maxDictTxt":maxDictionaryText, 
                                "minNumPlays":minNumPlays,
                                "minNumPlaysErrorMsg":minNumPlaysErrorMsg}
    
    return jsCode


def generateEmbed(wavDir, fnList):
    embedTxt = ""
    for fnFullPath in fnList:
        fn = os.path.split(fnFullPath)[1]
        name = os.path.splitext(fn)[0]
        
        basePath = os.path.join(wavDir, name)

        oggFN = basePath + ".ogg"
        mp3FN = basePath + ".mp3"
        
        embedTxt += embedTemplate % (name, oggFN, mp3FN)
    return embedTxt

    
def generateAudioButton(name, idNum, example=False):
    if example:
        template = buttonTemplateExample
    else:
        template = buttonTemplate

    template = template % {'button_label': loader.getText('play button')}

    return template % (idNum, name, idNum)


def getSoundFileDuration(fn):
    '''
    Returns the duration of a wav file (in seconds)
    '''
    with contextlib.closing(wave.open(fn, "r")) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        
    return duration
    
    
if __name__ == "__main__":
    print getSoundFileDuration("../wav/apples.wav")
    
        