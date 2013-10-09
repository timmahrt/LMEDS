#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os
import constants

import wave
import contextlib

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
<input type="button" id="button%d" value="Play Sound" onClick="EvalSound('%s',this, true, '%d')">
"""
#<input type="button" value="Play Sound" onClick="EvalSound('%s',this, true, 2)">
#<input type="button" value="Play Sound" onClick="document.getElementById('%s').play()">

buttonTemplateExample = """
<input type="button" id="button%d" value="Play Sound" onClick="EvalSound('%s',this, false, '%d')">
"""


playAudioFileJS = '''
    <script>
var silence = %s;
var numSoundFiles = %d;
var countDict = {
%s
};
var maxDict = {
%s
};
function EvalSound(soundobj, button, silence, id) {
  audioFile = document.getElementById(soundobj);
  audioFile.currentTime = 0;
  audioFile.addEventListener('ended', enable);
  audioFile.play();

    for (var i=0;i<numSoundFiles;i++)
    { 
    document.getElementById("button"+i.toString()).disabled=true;
    }

  countDict[id] = countDict[id] + 1;
}
function enable() {
        for (var i=0; i<numSoundFiles;i++)
        {
        if (silence == false || countDict[i] < maxDict[i])
            {
            document.getElementById("button"+i.toString()).disabled=false;
            }
        }
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

def getPlayAudioJavaScript(doSilence, numItems, maxList):

    if doSilence:
        silenceTxt = 'true'
    else:
        silenceTxt = 'false'
    
    maxDictionaryTextList = []
    for i, maxV in enumerate(maxList):
        maxDictionaryTextList.append('"%s":%d,' % (i, maxV))
    maxDictionaryText = "\n".join(maxDictionaryTextList)
    
    dictionaryTextList = []
    for i in xrange(numItems):
        dictionaryTextList.append('"%s":0,' % (i))
    countDictionaryText = "\n".join(dictionaryTextList)
    

    
    jsCode = playAudioFileJS % (silenceTxt, numItems, countDictionaryText, maxDictionaryText)
    
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
        return buttonTemplateExample % (idNum, name, idNum)
    else:
        return buttonTemplate % (idNum, name, idNum)


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
    
        