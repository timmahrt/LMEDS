#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import types
import os
from os.path import join

import wave
import contextlib

from lmeds.lmeds_io import loader
from lmeds.utilities import constants
from lmeds.utilities import utils

_tmpButton = ('<input type="button" id="button%%d" '
              'value="%(button_label)s" '
              '''onClick="LmedsAudio.evalSound(this, true, '%%d', %%f, '%%s')">'''
              )

buttonTemplate = _tmpButton

_tmpButton = ('<input type="button" id="button%%d" '
              'value="%s" '
              '''onClick="LmedsAudio.evalSound(this, false, '%%d', %%f, '%%s')">'''
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

    </script>
'''


def getPlaybackJS(doSilence, numItems, maxNumPlays, minNumPlays,
                  autosubmit=False, runOnFinish=None, listenPartial=False,
                  runOnMinThreshold=None):

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
    for i in range(numItems):
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
        autoSubmitHTML = "audioFile.addEventListener('ended', auto_submit);"
    if runOnFinish is not None:
        autoSubmitHTML += "\n" + runOnFinish
    if runOnMinThreshold is None:
        runOnMinThreshold = ""
    
    minNumPlaysErrorMsg = errorMsg % int(minNumPlays)
    
    jsCode = playAudioFileJS % {"silenceFlag": silenceFlag,
                                "numSoundFiles": numItems,
                                "countDictTxt": countDictionaryText,
                                "minNumPlays": minNumPlays,
                                "maxNumPlays": maxNumPlays,
                                "minNumPlaysErrorMsg": minNumPlaysErrorMsg,
                                "autosubmit_code": autoSubmitHTML,
                                "listenPartialFlag": listenPartial,
                                'audioMinThresholdEvent': runOnMinThreshold}
    
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
if (typeof(LmedsAudio.load_audio) == "function") {
    LmedsAudio.load_audio();
    }
"""

# loading_progress_show() waits for the audio file(s) to be loaded before
# playing.  For whatever reason, firefox auto aborted so the audio would never
# load.  However, when someone clicked "play" firefox would load the content
# correctly.  Anyhow, it seems this code shouldn't be used for now (it's odd
# though because I thought it was working when I first wrote it).
# loadAudioSnippet_old_and_broken_on_firefox = """
loadAudioSnippet = """
if (typeof(LmedsAudio.load_audio) == "function") {
    LmedsAudio.loading_progress_show();
    LmedsAudio.mediaPath = "../tests/lmeds_demo/audio_and_video"
    LmedsAudio.load_audio();
    }
"""

    
def generateEmbed(wavDir, nameList, extList, audioOrVideo):
    
    if not os.path.exists(wavDir):
        raise PathDoesNotExist(wavDir)
    
    for name in nameList:
        fnList = [name + ext for ext in extList]
        if any([not os.path.exists(join(wavDir, fn))
                for fn in fnList]):
            raise utils.FilesDoNotExist(wavDir, fnList, True)
    
    nameSet = set(nameList)
    nameList = ["'%s'" % os.path.splitext(os.path.split(name)[1])[0]
                for name in nameSet]
    nameTxtList = "[%s]" % (','.join(nameList))
    
    extList = ["'%s'" % ext for ext in extList]
    extTxtList = "[%s]" % (','.join(extList))
    
    embedTxt = '''
<script>
LmedsAudio.media_type = "%(mediaType)s";
LmedsAudio.media_path = "%(path)s";
LmedsAudio.extensionList = %(extensionList)s;
LmedsAudio.audioList = %(nameList)s;
</script>
''' % {'extensionList': extTxtList,
       'nameList': nameTxtList,
       'path': wavDir.replace("\\", "/"),  # We use '/' regardless of OS
       'mediaType': audioOrVideo,
       }
    
    return embedTxt

    
def generateAudioButton(name, idNum, pauseDurationSec=0, example=False):
    
    # Accept 'name' to be a list, but if it is, convert it into a string
    
    # Python 2-to-3 compatibility hack
    
    if isinstance(name, constants.list):
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
