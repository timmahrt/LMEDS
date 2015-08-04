#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import types
import os
from os.path import join

import wave
import contextlib

from lmeds.io import loader

embedTemplate = ('<audio id="%s" preload="none" '
                 'oncanplaythrough="increment_audio_loaded_count()">'
                 '<source src="%s" type="audio/ogg">'
                 '<source src="%s" type="audio/mpeg">'
                 '</audio>'
                 )

_tmpButton = ('<input type="button" id="button%%d" '
              'value="%(button_label)s" '
              '''onClick="EvalSound(this, true, '%%d', %%f, '%%s')">'''
              )

buttonTemplate = _tmpButton

_tmpButton = ('<input type="button" id="button%%d" '
              'value="%s" '
              '''onClick="EvalSound(this, false, '%%d', %%f, '%%s')">'''
              )

buttonTemplateExample = _tmpButton % 'false'

playAudioFileJS = '''
    <script>
var silenceFlag = %(silenceFlag)s;
var numSoundFiles = %(numSoundFiles)d;
var numUniqueSoundFiles = $("audio").length;
var numSoundFilesLoaded = 0;
var finishedLoading = false;
var doingPandBPage = false;
var listenPartial = %(listenPartialFlag)s;

var countDict = {
%(countDictTxt)s
};
var myTxt = "";
function increment_audio_loaded_count() {
    numSoundFilesLoaded = numSoundFilesLoaded + 1;
    updateProgress(100*(numSoundFilesLoaded / numUniqueSoundFiles));
    if (numSoundFilesLoaded >= numUniqueSoundFiles) {
        loading_progress_hide();
        audio_buttons_enable();
        finishedLoading = true;
    }
    //alert(numSoundFilesLoaded + ' - ' + numUniqueSoundFiles);
    myTxt = myTxt + "\\n" + this.id;
    //alert(myTxt);
    this.removeEventListener('canplay', increment_audio_loaded_count);
    this.removeEventListener('error', catchFailedAudioLoad);
    
}
function EvalSound() {
  
  var button = arguments[0];
  var silenceFlag = arguments[1];
  var id = arguments[2];
  var pauseDurationMS = arguments[3] * 1000;
  
  var audioListArray = arguments[4].split(',');

  recPlayAudioList(audioListArray, pauseDurationMS);

  audio_buttons_disable()

  var tmpId = 'audioFilePlays'+id.toString()
  var numTimesPlayed = parseInt(document.getElementById(tmpId).value)
  document.getElementById(tmpId).value = numTimesPlayed + 1;
  countDict[id] = countDict[id] + 1;
  
  // Enable the submit button if listeners only need to listen to a portion
  // of the audio (e.g. in an audio test)
  if (document.getElementById("submitButton") !== null)
  {
    if (listenPartial == true)
    {
      // Enable the submit button if at least the minimum number of plays is
      // completed for all audio files
      var allGreater = true;
      if (silenceFlag == true && %(minNumPlays)d > 0)
      {
        if (doingPandBPage == true) {
          if (%(minNumPlays)d <= countDict[0]) {
            document.getElementById("halfwaySubmitButton").disabled=false;
            doingPandBPage = false;
          }
        }
        else {
        
          for (var i=0;i<numSoundFiles;i++) {
            if (%(minNumPlays)d > countDict[i]) {
              allGreater = false;
            }
          }
        
          if (allGreater == true) {
            document.getElementById("submitButton").disabled=false;
          }
        }
      }
    }
  }
  
  return false;
}
function updateProgress(percentComplete) {
    var percentUncomplete = 100 - percentComplete;
    var percentCompleteStr = percentComplete.toString() + "%%";
    var percentUncompleteStr = percentUncomplete.toString() + "%%";
    $('#loading_percent_done').css('width', percentCompleteStr);
    $('#loading_percent_left').css('width', percentUncompleteStr);
}
function recPlayAudioList(audioList, pauseDurationMS) {
    var soundobj = audioList.shift();
    var audioFile = document.getElementById(soundobj);
    audioFile.currentTime = 0;
    audioFile.play();

    var timeout = pauseDurationMS + (1000 * audioFile.duration);

    // When the last audio finishes playing, running any post-audio operations
    if (audioList.length == 0) {
        setTimeout(function(){
        audioFile.addEventListener('ended', audio_buttons_enable);
        %(autosubmit_code)s
        }, timeout - pauseDurationMS);
    }
    
    // After the audio has finished playing, play the next file in the list
    if (audioList.length > 0) {
        setTimeout(function(){recPlayAudioList(audioList, pauseDurationMS);},
                   timeout);
    }

}

function loading_progress_show() {
$("#loading_status_indicator").show();
}
function loading_progress_hide()
{
    // Disable the submit button if needed
    if (document.getElementById("submitButton") !== null)
    {
      if (%(minNumPlays)d > 0)
      {
        document.getElementById("submitButton").disabled=true;
        if (document.getElementById("halfwaySubmitButton") !== null)
        {
          document.getElementById("halfwaySubmitButton").disabled=true;
          doingPandBPage = true;
        }
      }
    }
    
    $("#loading_status_indicator").hide();
}

function audio_buttons_disable() {
  for (var j=0;j<numSoundFiles;j++) {
    document.getElementById("button"+j.toString()).disabled=true;
  }
}

function audio_buttons_enable()
{
  var silence = silenceFlag == false;
    for (var i=0; i<numSoundFiles;i++)
    {
        if (silence || %(maxNumPlays)d < 0 || countDict[i] < %(maxNumPlays)d) {
          document.getElementById("button"+i.toString()).disabled=false;
          }
        else {
          document.getElementById("button"+i.toString()).disabled=true;
        }
        }
        
      // Enable the submit button if at least the minimum number of plays is
      // completed for all audio files
     if (document.getElementById("submitButton") !== null)
     {
      var allGreater = true;
      if (silenceFlag == true && %(minNumPlays)d > 0)
      {
        if (doingPandBPage == true) {
          if (%(minNumPlays)d <= countDict[0]) {
            document.getElementById("halfwaySubmitButton").disabled=false;
            doingPandBPage = false;
          }
        }
        else {
        
          for (var i=0;i<numSoundFiles;i++) {
            if (%(minNumPlays)d > countDict[i]) {
              allGreater = false;
            }
          }
        
          if (allGreater == true) {
            document.getElementById("submitButton").disabled=false;
          }
        }
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


def getPlaybackJS(doSilence, numItems, maxNumPlays, minNumPlays,
                  autosubmit=False, runOnFinish=None, listenPartial=False):

    maxNumPlays = int(maxNumPlays)
    minNumPlays = int(minNumPlays)

    if doSilence:
        silenceFlag = 'true'
    else:
        silenceFlag = 'false'
        
    if listenPartial:
        listenPartial = "true"
    else:
        listenPartial = "false"
    
    dictionaryTextList = []
    for i in xrange(numItems):
        dictionaryTextList.append('"%s":0,' % (i))
    countDictionaryText = "\n".join(dictionaryTextList)
    
    # Get error message and make sure it is formatted correctly
    if minNumPlays < maxNumPlays:  # Upper and lower-bound
        errorKey = "error_must_play_audio_at_least"
    else:  # No upper-bound
        errorKey = "error_must_play_audio"
        
    errorMsg = loader.getText(errorKey)
    if "%d" not in errorMsg:
        # Error message from the developer
        badFormattedText = ("Please add a '%d', for the minimum number of "
                            "required audio plays, in the text file"
                            )
        raise loader.BadlyFormattedTextError(badFormattedText, errorKey)
    
    autoSubmitHTML = ""
    if autosubmit is True:
        autoSubmitHTML = "setTimeout(function(){processSubmit()}, timeout);"
    if runOnFinish is not None:
        autoSubmitHTML += "\n" + runOnFinish
    
    minNumPlaysErrorMsg = errorMsg % int(minNumPlays)
    
    jsCode = playAudioFileJS % {"silenceFlag": silenceFlag,
                                "numSoundFiles": numItems,
                                "countDictTxt": countDictionaryText,
                                "minNumPlays": minNumPlays,
                                "maxNumPlays": maxNumPlays,
                                "minNumPlaysErrorMsg": minNumPlaysErrorMsg,
                                "autosubmit_code": autoSubmitHTML,
                                "listenPartialFlag": listenPartial}
    
    return jsCode


class PathDoesNotExist(Exception):
    
    def __init__(self, path):
        super(PathDoesNotExist, self).__init__()
        self.path = path
        
    def __str__(self):
        return "ERROR: Folder, %s, does not exist" % self.path


class FileNotFound(Exception):
    
    def __init__(self, fnFullPath):
        super(FileNotFound, self).__init__()
        self.fn = fnFullPath
    
    def __str__(self):
        return "ERROR: File, %s, does not exist" % self.fn
    
    
loadAudioSnippet_no_progress_bar = """
if (typeof(load_audio) == "function") {
    load_audio();
    }
"""

# loading_progress_show() waits for the audio file(s) to be loaded before
# playing.  For whatever reason, firefox auto aborted so the audio would never
# load.  However, when someone clicked "play" firefox would load the content
# correctly.  Anyhow, it seems this code shouldn't be used for now (it's odd
# though because I thought it was working when I first wrote it).
# loadAudioSnippet_old_and_broken_on_firefox = """
loadAudioSnippet = """
if (typeof(load_audio) == "function") {
    loading_progress_show();
    load_audio();
    }
"""

    
def generateEmbed(wavDir, fnList):
    
    if not os.path.exists(wavDir):
        raise PathDoesNotExist(wavDir)
        
    for fn in fnList:
        fnFullPath = join(wavDir, fn + ".ogg")
        if not os.path.exists(fnFullPath):
            raise FileNotFound(fnFullPath)
    
    fnSet = set(fnList)
    nameList = ["'%s'" % os.path.splitext(os.path.split(fn)[1])[0]
                for fn in fnSet]
    nameTxtList = "[%s]" % (','.join(nameList))
    
    embedTxt = '''
<script>
var catchFailedAudioLoad = function(e) {
    var errorMsg = "There was a problem with file: " + this.src;
    var specErrorMsg;
   // audio playback failed - show a message saying why
   // to get the source of the audio element use $(this).src
   switch (e.target.error.code) {
     case e.target.error.MEDIA_ERR_ABORTED:
       
       specErrorMsg = 'You aborted the video playback.';
       break;
     case e.target.error.MEDIA_ERR_NETWORK:
       specErrorMsg = 'A network error caused the audio download to fail.';
       break;
     case e.target.error.MEDIA_ERR_DECODE:
       specErrorMsg = 'The audio playback was aborted due to a corruption ' +
                      'problem or because the video used features your ' +
                      'browser did not support.';
       break;
     case e.target.error.MEDIA_ERR_SRC_NOT_SUPPORTED:
       specErrorMsg = 'The video audio not be loaded, either because the ' +
                      'server or network failed or because the format is ' +
                      'not supported.';
       break;
     default:
       specErrorMsg = 'An unknown error occurred.';
       break;
   }
   alert(errorMsg + "\\n\\n" + specErrorMsg);
}
var audio_list = [];
function load_audio() {
    var audioList = %(nameList)s;
    numUniqueSoundFiles = audioList.length;
    for (var j=0; j<audioList.length;j++) {
        var audioName = audioList[j];
        var audio = document.createElement('audio');
        audio.id = audioName;
        
        
        if (audio.canPlayType('audio/ogg')) {
            audio.type= 'audio/ogg';
            audio.src= '%(path)s/' + audioName + '.ogg';
        } else {
            audio.type= 'audio/mpeg';
            audio.src= '%(path)s/' + audioName + '.mp3';
        }
        /*
        if (audio.canPlayType('audio/mpeg')) {
            audio.type= 'audio/mpeg';
            audio.src= '%(path)s/' + audioName + '.mp3';
        } else {
            audio.type= 'audio/ogg';
            audio.src= '%(path)s/' + audioName + '.ogg';
        }*/
        
        audio.preload = 'auto';
        document.getElementById('audio_hook').appendChild(audio);
        audio.addEventListener('canplay', increment_audio_loaded_count);
        audio.addEventListener('error', catchFailedAudioLoad);
        audio_list.push(audio);
        audio.load();
    }
}
</script>
''' % {'nameList': nameTxtList,
       'path': wavDir.replace("\\", "/")  # We use '/' regardless of OS
       }
    
    return embedTxt

    
def generateAudioButton(name, idNum, pauseDurationSec=0, example=False):
    
    # Accept 'name' to be a list, but if it is, convert it into a string
    if isinstance(name, types.ListType):
        name = ",".join(name)
        
    if example:
        template = buttonTemplateExample
    else:
        template = buttonTemplate

    template = template % {'button_label': loader.getText('play_button')}

    return template % (idNum, idNum, float(pauseDurationSec), name)


def getSoundFileDuration(fn):
    '''
    Returns the duration of a wav file (in seconds)
    '''
    with contextlib.closing(wave.open(fn, "r")) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        
    return duration
