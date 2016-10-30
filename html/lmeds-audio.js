

var LmedsAudio = function () {

    // lmeds.audio internal variables
    var mime_type_dict = {
        	".mp3":"mpeg",
        	".mp4":"mpeg",
        	".webm":"webm",
        	".ogg":"ogg"};
    var media_type_dict = {AUDIO:"audio", VIDEO:"video"};
    var audio_list = [];  // The actual audio file objects
    var numSoundFilesLoaded = 0;
    var numUniqueSoundFiles = 0;
    var finishedLoading = false;
    var autosubmit = true;
    
    // lmeds.audio public variables
    var media_path = "";
    var media_type = "";
    var extensionList = [];

    var media_type = media_type_dict.AUDIO;
    var audioList = []; // Audio file names

    var minNumPlays = -1;
    var maxNumPlays = -1;
    var minNumPlaysErrMsg = "";
    var countDict = {};

    
    function load_audio() {
    	mime_type_dict[".mpg"]
        numUniqueSoundFiles = this.audioList.length;
        numBlah = audio_list.length;
        // Recreate the counting dictionary
        countDict = {};
        for (var j=0; j < this.audioList.length; j++) {
        	countDict[j] = 0;
        }
        
//        var mime_type_dict = {".wav":"wav",
//                ".mp3":"mpeg",
//                ".mp4":"mpeg",
//                ".webm":"webm",
//                ".ogg":"ogg"};
        
        var t = mime_type_dict[".mp3"]
        
        for (var j=0; j < this.audioList.length; j++) {
            var audioName = this.audioList[j];
            var audio = document.createElement(this.media_type);
            audio.id = audioName;
            
            var source = document.createElement('source');
            
            for (var k=0; k < this.extensionList.length; k++) {
                // Audio acts in a FILO manner, so iterate the list backwards
                // to get the user's order preference.
                var tmpExt = this.extensionList[this.extensionList.length - (k + 1)];
                source.type = this.media_type + '/' + mime_type_dict[tmpExt];
                source.src = this.media_path + '/' + audioName + tmpExt;
                audio.appendChild(source)
            }
            
            audio.preload = 'auto';
            document.getElementById('audio_hook').appendChild(audio);
            audio.addEventListener('canplay', increment_audio_loaded_count);
            audio.addEventListener('error', catchFailedAudioLoad);
            audio_list.push(audio);
            audio.load();
        }
    }
    
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
    
    function audio_buttons_enable(e = null) {
      // if audio_buttons_enable is a handler for an event listener, once it is
      // called, it should remove itself as a handler until it is told to listen
      // again.
      if (e != null) {
        e.target.removeEventListener('ended', this.audio_buttons_enable);
      }

      var silence = silenceFlag == false;
        for (var i=0; i < numSoundFiles;i++)
        {
            if (silence || maxNumPlays < 0 || countDict[i] < maxNumPlays) {
              document.getElementById("button"+i.toString()).disabled=false;
              }
            else {
              document.getElementById("button"+i.toString()).disabled=true;
            }
            }
            
          // Enable the submit button if at least the minimum number of plays is
          // completed for all audio files
         
         {
          var allGreater = true;
          if (silenceFlag == true && this.minNumPlays > 0)
          {
            if (doingPandBPage == true) {
              if (this.minNumPlays <= countDict[0]) {
                if (document.getElementById("submitButton") !== null) {
                    document.getElementById("halfwaySubmitButton").disabled=false;
                    doingPandBPage = false;
                }
              }
            }
            else {
            
              for (var i=0;i<numSoundFiles;i++) {
                if (this.minNumPlays > countDict[i]) {
                  allGreater = false;
                }
              }
            
              if (allGreater == true) {
                  if (document.getElementById("submitButton") !== null) {
                    document.getElementById("submitButton").disabled=false;
                  }
                  //%(audioMinThresholdEvent)s
              }
            }
          }
          else
          {
          //%(audioMinThresholdEvent)s
          }
        }
        
    }

    function increment_audio_loaded_count() {
        numSoundFilesLoaded += 1;
        updateProgress(100*(numSoundFilesLoaded / numUniqueSoundFiles));
        if (numSoundFilesLoaded >= numUniqueSoundFiles) {
            loading_progress_hide();
            audio_buttons_enable();
            finishedLoading = true;
        }
        //alert(numSoundFilesLoaded + ' - ' + numUniqueSoundFiles);
        //myTxt = myTxt + "\\n" + this.id;
        //alert(myTxt);
        removeEventListener('canplay', this.increment_audio_loaded_count);
        removeEventListener('error', this.catchFailedAudioLoad);
        
    }
    
    function evalSound(button, silenceFlag, id, pauseDurationMS, audioListTxt) {
      
      //var button = arguments[0];
      //var silenceFlag = arguments[1];
      //var id = arguments[2];
      //var pauseDurationMS = arguments[3] * 1000;
      
      var audioList = audioListTxt.split(',');

      recPlayAudioList(audioList, pauseDurationMS);

      audio_buttons_disable()

      var tmpId = 'audioFilePlays'+id.toString()
      var numTimesPlayed = parseInt(document.getElementById(tmpId).value)
      document.getElementById(tmpId).value = numTimesPlayed + 1;
      countDict[id] += 1;
      
      // Enable the submit button if listeners only need to listen to a portion
      // of the audio (e.g. in an audio test)
      if (document.getElementById("submitButton") !== null)
      {
        if (listenPartial == true)
        {
          // Enable the submit button if at least the minimum number of plays is
          // completed for all audio files
          var allGreater = true;
          if (silenceFlag == true && this.minNumPlays > 0)
          {
            if (doingPandBPage == true) {
              if (this.minNumPlays <= countDict[0]) {
                document.getElementById("halfwaySubmitButton").disabled=false;
                doingPandBPage = false;
              }
            }
            else {
            
              for (var i=0;i<numSoundFiles;i++) {
                if (this.minNumPlays > countDict[i]) {
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

        // After the audio has finished playing, play the next file in the list
        if (audioList.length > 0) {
            setTimeout(function(){recPlayAudioList(audioList, pauseDurationMS);},
                       timeout);
        }
        // When the last audio finishes playing, running any post-audio operations
        else if (audioList.length == 0) {
            audioFile.addEventListener('ended', audio_buttons_enable);
            if(autosubmit == true) {
            	audioFile.addEventListener('ended', auto_submit);
            }
        }

    }
    function auto_submit(e) {
        e.target.removeEventListener('ended', auto_submit);
        processSubmit()
    }
    function loading_progress_show() {
    $("#loading_status_indicator").show();
    }
    function loading_progress_hide()
    {
        // Disable the submit button if needed
        if (document.getElementById("submitButton") !== null)
        {
          if (this.minNumPlays > 0)
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
    
    function verifyAudioPlayed() {
        var doAlert = false;
        var returnValue = true;
        for (var i=0; i<numSoundFiles;i++)
        {
        if (countDict[i] < this.minNumPlays)
            {
            doAlert = true;
            }
        }
            
        if (doAlert == true) {
            alert(this.minNumPlaysErrMsg);
            returnValue = false;
        }

        return returnValue;
    }
    
    function verifyFirstAudioPlayed() {
        var returnValue = true;
        if(countDict["0"] < this.minNumPlays)
        {
        alert(this.minNumPlaysErrMsg);
        returnValue = false;
        }
        return returnValue;
    }
    
    function audio_buttons_disable() {
    	  for (var j=0;j<numSoundFiles;j++) {
    	    document.getElementById("button"+j.toString()).disabled=true;
    	  }
    	}
    
    return {
    	
    	// public variables
        media_type_dict: media_type_dict,
        media_type: media_type,
        media_path: media_path,
        minNumPlays: minNumPlays,
        maxNumPlays: maxNumPlays,
        minNumPlaysErrMsg: minNumPlaysErrMsg,
        audioList: audioList,
        extensionList: extensionList,
        autosubmit: autosubmit,

        // public functions
        load_audio: load_audio,
        evalSound: evalSound,
        loading_progress_show: loading_progress_show,
        loading_progress_hide: loading_progress_hide,
        verifyAudioPlayed: verifyAudioPlayed,
    }

}();
