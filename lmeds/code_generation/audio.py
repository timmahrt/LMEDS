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
              '''onClick="audioLoader.evalSound(this, '%%d', %%f, '%%s', %%s)">'''
              )

buttonTemplate = _tmpButton

_tmpButton = ('<input type="button" id="button%%d" '
              'value="%s" '
              '''onClick="audioLoader.evalSound(this, '%%d', %%f, '%%s', %%s)">'''
              )

buttonTemplateExample = _tmpButton % 'false'

playAudioFileJS = '''
// Various page-specific parameters
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

'''


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
// Load the audio
if (typeof(audioLoader.load_audio) == "function") {
    audioLoader.load_audio();
    }\n
"""

# loading_progress_show() waits for the audio file(s) to be loaded before
# playing.  For whatever reason, firefox auto aborted so the audio would never
# load.  However, when someone clicked "play" firefox would load the content
# correctly.  Anyhow, it seems this code shouldn't be used for now (it's odd
# though because I thought it was working when I first wrote it).
# loadAudioSnippet_old_and_broken_on_firefox = """
loadAudioSnippet = """
// Load the audio
if (typeof(audioLoader.load_audio) == "function") {
    audioLoader.loading_progress_show();
    audioLoader.load_audio();
    }\n
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
// Set the parameters for working with media files
audioLoader = new LmedsAudio();
audioLoader.media_type = "%(mediaType)s";
audioLoader.media_path = "%(path)s";
audioLoader.extensionList = %(extensionList)s;
audioLoader.audioList = %(nameList)s;\n
''' % {'extensionList': extTxtList,
       'nameList': nameTxtList,
       'path': wavDir.replace("\\", "/"),  # We use '/' regardless of OS
       'mediaType': audioOrVideo,
       }
    
    return embedTxt

    
def generateAudioButton(name, idNum, buttonLabel, pauseDurationSec=0,
                        example=False, autoSubmit=False):
    
    # Accept 'name' to be a list, but if it is, convert it into a string
    
    # Python 2-to-3 compatibility hack
    
    if isinstance(name, constants.list):
        name = ",".join(name)
    
    if example:
        template = buttonTemplateExample
    else:
        template = buttonTemplate
        
    if autoSubmit is False:
        autoSubmit = "false"
    elif autoSubmit is True:
        autoSubmit = "true"

    template = template % {'button_label': buttonLabel}

    return template % (idNum, idNum, float(pauseDurationSec), name, autoSubmit)


def getSoundFileDuration(fn):
    '''
    Returns the duration of a wav file (in seconds)
    '''
    with contextlib.closing(wave.open(fn, "r")) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        
    return duration
