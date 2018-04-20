
var LmedsAudio = function() {
    this.elem = document.createElement('div');
    // lmeds.audio internal variables
    this.mime_type_dict = {
        ".mp3": "mpeg",
        ".mp4": "mpeg",
        ".webm": "webm",
        ".ogg": "ogg",
        ".wav": "wav",
    };
    this.media_type_dict = {
        AUDIO: "audio",
        VIDEO: "video"
    };
    this.audio_list = []; // The actual audio file objects
    this.numSoundFilesLoaded = 0;
    this.numUniqueSoundFiles = 0;
    this.numAudioButtons = 0;
    this.finishedLoading = false;
    this.silenceFlag = true;
    this.listenPartial = false;

    this.doingBAndPPage = false;

    // lmeds.audio public variables
    this.media_path = "";
    this.media_type = "";
    this.extensionList = [];

    this.minPlayFuncList = [];

    this.media_type = this.media_type_dict.AUDIO;
    this.audioList = []; // Audio file names

    this.minNumPlays = -1;
    this.maxNumPlays = -1;
    this.minNumPlaysErrMsg = "";
    this.countDict = {};

    this.evalSound = this.evalSound.bind(this)
    this.increment_audio_loaded_count = this.increment_audio_loaded_count.bind(this)
    this.catchFailedAudioLoad = this.catchFailedAudioLoad.bind(this)
    this.audio_buttons_enable = this.audio_buttons_enable.bind(this)
    this.auto_submit = this.auto_submit.bind(this)
};

LmedsAudio.prototype.load_audio = function() {

    // Recreate the counting dictionary
    this.countDict = {};
    for (var j = 0; j < this.numAudioButtons; j++) {
        this.countDict[j] = 0;
    }

    for (var j = 0; j < this.numUniqueSoundFiles; j++) {
        var audioName = this.audioList[j];
        var audio = document.createElement(this.media_type);
        audio.id = audioName;

        var source = document.createElement('source');

        for (var k = 0; k < this.extensionList.length; k++) {
        	var tmpExt = this.extensionList[k];
        	var mimeType = this.media_type + '/' + this.mime_type_dict[tmpExt];
        	
        	// Choose the first type available that will work with this browser
        	if (audio.canPlayType(mimeType + ';')) {
        	    source.type = mimeType;
        	    source.src= this.media_path + '/' + audioName + tmpExt;
        	    audio.appendChild(source)
        	    break;
        	}
        }

        audio.preload = 'auto';
        document.getElementById('audio_hook').appendChild(audio);

        audio.addEventListener('canplay', this.increment_audio_loaded_count);
        audio.addEventListener('error', this.loadErrorHandler);
        this.audio_list.push(audio);
        
        audio.load();
    }
}

LmedsAudio.prototype.catchFailedAudioLoad = function(e) {
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

LmedsAudio.prototype.minButtonPressSatisfied = function() {
    var allGreater = true;
    for (var i = 0; i < this.numAudioButtons; i++) {
        if (this.minNumPlays > this.countDict[i]) {
            allGreater = false;
        }
    }
    return allGreater;
}

LmedsAudio.prototype.audio_buttons_enable = function(e) {
    // if audio_buttons_enable is a handler for an event listener, once it is
    // called, it should remove itself as a handler until it is told to listen
    // again.
    if (typeof e != 'undefined' && e != null) {
        e.target.removeEventListener('ended', this.audio_buttons_enable);
    }

    var silence = this.silenceFlag == false;
    for (var i = 0; i < this.numAudioButtons; i++) {
        if (silence || this.maxNumPlays < 0 || this.countDict[i] < this.maxNumPlays) {
            document.getElementById("button" + i.toString()).disabled = false;
        } else {
            document.getElementById("button" + i.toString()).disabled = true;
        }
    }

    // Enable the submit button if at least the minimum number of plays is
    // completed for all audio files
    if (this.silenceFlag == true && this.minNumPlays > 0) {

        if (this.doingBAndPPage == true) {
            if (this.minNumPlays <= this.countDict[0]) {
                document.getElementById("halfwaySubmitButton").disabled = false;
                this.doingBAndPPage = false;
            }
        } else {
            var allGreater = this.minButtonPressSatisfied();
            if (allGreater == true) {
                for (var i = 0; i < this.minPlayFuncList.length; i++) {
                    this.minPlayFuncList[i]();
                }
                enableSubmitButton(this, true);
            }
        }
    } else {
        for (var i = 0; i < this.minPlayFuncList.length; i++) {
            this.minPlayFuncList[i]();
        }
        enableSubmitButton(this, true);
    }
}

LmedsAudio.prototype.increment_audio_loaded_count = function(e) {
    this.numSoundFilesLoaded += 1;
    this.updateProgress(100 * (this.numSoundFilesLoaded / this.numUniqueSoundFiles));

    e.target.removeEventListener('canplay', this.increment_audio_loaded_count);
    e.target.removeEventListener('error', this.loadErrorHandler);
    if (this.numSoundFilesLoaded >= this.numUniqueSoundFiles) {
        this.loading_progress_hide();
        this.audio_buttons_enable();
        this.finishedLoading = true;
    }
}

LmedsAudio.prototype.evalSound = function(button, id, pauseDurationMS, audioListTxt, autoSubmit) {

    var audioList = audioListTxt.split(',');

    this.recPlayAudioList(audioList, pauseDurationMS, autoSubmit, this);

    this.audio_buttons_disable()

    var tmpId = 'audioFilePlays' + id.toString()
    var numTimesPlayed = parseInt(document.getElementById(tmpId).value)
    document.getElementById(tmpId).value = numTimesPlayed + 1;
    this.countDict[id] += 1;

    enableSubmitButton(this, false);

    return false;
}

enableSubmitButton = function(audioLoader, isCompleted) {

    var enableHalfwaysubmit = false;
    var enableSubmit = false;

    // If any of the following conditions are true, we need to check
    // that the buttons have been pressed the appropriate 

    // Does the page present audio?
    var audioOptional = audioLoader.silenceFlag == false; // There is no audio
    audioOptional |= audioLoader.listenPartial == true; // Or there is audio, but it's not required to listen to it
    audioOptional |= audioLoader.minNumPlays == -1; // Or there is audio, but listeners can listen to it any number of times

    var minPlaysDone = audioLoader.minNumPlays > 0; // Is a minimum num plays required?
    minPlaysDone &= isCompleted == true; // And are we ready to continue to the next page?

    if (document.getElementById("submitButton") !== null) {

        // There are no audio buttons (or the audio buttons are optional)
        // (or the audio doesn't need to play all the way through)
        // then the submit button should just be enabled
        if (audioOptional == true && audioLoader.doingBAndPPage == true) {
            enableHalfwaysubmit = true;
        } else if (audioOptional == true && audioLoader.doingBAndPPage == false) {
            enableSubmit = true;
        }
        // There are audio buttons.  Enable the submit button if there
        else if (minPlaysDone == true && audioLoader.doingBAndPPage == true) {
            if (audioLoader.minNumPlays <= audioLoader.countDict[0]) {
                enableHalfwaysubmit = true;
            }
        } else if (minPlaysDone == true && audioLoader.doingBAndPPage == false) {
            var allGreater = audioLoader.minButtonPressSatisfied();
            if (allGreater == true) {
                enableSubmit = true;
            }
        }
    }

    // Here is where we enable the appropriate button
    if (enableHalfwaysubmit == true) {
        document.getElementById("halfwaySubmitButton").disabled = false;
        audioLoader.doingBAndPPage = false;
    } else if (enableSubmit == true) {
        document.getElementById("submitButton").disabled = false;
    }
}

LmedsAudio.prototype.updateProgress = function(percentComplete) {
    var percentUncomplete = 100 - percentComplete;
    var percentCompleteStr = percentComplete.toString() + "%%";
    var percentUncompleteStr = percentUncomplete.toString() + "%%";
    $('#loading_percent_done').css('width', percentCompleteStr);
    $('#loading_percent_left').css('width', percentUncompleteStr);
}

LmedsAudio.prototype.recPlayAudioList = function(audioList, pauseDurationMS, autoSubmit, me) {
    var soundobj = audioList.shift();
    var audioFile = document.getElementById(soundobj);
    audioFile.currentTime = 0;
    audioFile.play();

    var timeout = pauseDurationMS + (1000 * audioFile.duration);

    // After the audio has finished playing, play the next file in the list
    if (audioList.length > 0) {
        setTimeout(function() {
                me.recPlayAudioList(audioList, pauseDurationMS, autoSubmit, me);
            },
            timeout);
    }
    // When the last audio finishes playing, running any post-audio operations
    else if (audioList.length == 0) {
        audioFile.addEventListener('ended', me.audio_buttons_enable);
        if (autoSubmit == true) {
            audioFile.addEventListener('ended', me.auto_submit);
        }
    }
}

LmedsAudio.prototype.auto_submit = function(e) {
    e.target.removeEventListener('ended', this.auto_submit);
    processSubmit()
}

LmedsAudio.prototype.loading_progress_show = function() {
    $("#loading_status_indicator").show();
}

LmedsAudio.prototype.loading_progress_hide = function() {
    // Disable the submit button if needed
    if (document.getElementById("submitButton") !== null) {
        if (this.minNumPlays > 0) {
            document.getElementById("submitButton").disabled = true;
            if (document.getElementById("halfwaySubmitButton") !== null) {
                document.getElementById("halfwaySubmitButton").disabled = true;
                this.doingBAndPPage = true;
            }
        }
    }

    $("#loading_status_indicator").hide();
}

LmedsAudio.prototype.verifyAudioPlayed = function() {
    var doAlert = false;
    var returnValue = true;
    for (var i = 0; i < this.numAudioButtons; i++) {
        if (this.countDict[i] < this.minNumPlays) {
            doAlert = true;
        }
    }

    if (doAlert == true) {
        alert(this.minNumPlaysErrMsg);
        returnValue = false;
    }

    return returnValue;
}

LmedsAudio.prototype.verifyFirstAudioPlayed = function() {
    var returnValue = true;
    if (this.countDict["0"] < this.minNumPlays) {
        alert(this.minNumPlaysErrMsg);
        returnValue = false;
    }
    return returnValue;
}

LmedsAudio.prototype.audio_buttons_disable = function() {
    for (var j = 0; j < this.numAudioButtons; j++) {
        document.getElementById("button" + j.toString()).disabled = true;
    }
}
