
makeWordsVisibleCheckboxes = function(isProminence) {
    $('input[type=checkbox]').click(function() {
        if (isProminence == true) {
            $(this).closest("label").css({
                color: this.checked ? "red" : "black"
            });
        } else {
            $(this).closest("label").css({
                borderRight: this.checked ? "3px solid #000000" : "0px solid #FFFFFF"
            });
            $(this).closest("label").css({
                paddingRight: this.checked ? "0px" : "3px"
            });
        }
    });
}

removeCheckboxHandler = function() {
    $('input[type=checkbox]').off();
}

toggle = function() {
    $(this).closest("label").css({
        borderRight: this.checked ? "3px solid #000000" : "0px solid #FFFFFF"
    });
    $(this).closest("label").css({
        paddingRight: this.checked ? "0px" : "3px"
    });
}

blah = function() {
    $(this).next("span").css({
        visibility: this.checked ? "visible" : "hidden"
    });
}

blah2 = function() {
    $("#" + x).next("span").css({
        visibility: "visible"
    });
}

var didShowHide = false;
ShowHide = function(didAudioPlay, isWithinRange) {
    var didPlay = didAudioPlay;
    didPlay &= isWithinRange;
    if (didPlay == true) {
        didShowHide = true;
        document.getElementById("ShownDiv").style.display = 'none';
        document.getElementById("HiddenDiv").style.display = 'block';
        document.getElementById("HiddenForm").style.display = 'block';
        for (e = 0; e < 8; e++) {
            var x = e + 8;

            if (document.getElementById(e).checked == true) {

                $("#" + x).closest("label").css({
                    borderRight: "3px solid #000000"
                });
                $("#" + x).closest("label").css({
                    paddingRight: "0px"
                });

            }
        }
        removeCheckboxHandler();
        makeWordsVisibleCheckboxes(true);
    }

    $('html, body').animate({
        scrollTop: 0
    }, 'fast');
}


getHowManyMarked = function(startI, endI, widgetName) {
    var numMarked = 0;
    var chboxList = document.getElementsByName(widgetName);
    for (var i = startI; i < endI; i++) {
        if (chboxList[i].checked == true) {
            numMarked++;
        }
    }
    return numMarked;
}

isPBMarkingTask = function() {
    var markingTaskArray = [false, false];
    if (document.getElementById("submitButton") !== null) {
        if (document.getElementById("halfwaySubmitButton") !== null) {
            markingTaskArray[0] = true;
            if (didShowHide == true) {
                markingTaskArray[1] = true;
            }
        }
    }

    return markingTaskArray;
}

verifySelectedWithinRange = function(min_to_mark, max_to_mark, widgetName, minErrMsg, maxErrMsg, minMaxErrMsg) {

    var returnValue = true;
    var min = 0;
    var max = document.getElementsByName(widgetName).length;

    // If doing both b and p marking, we need to divide the max value by two.
    // If doing the 2nd half (p marking) we need to shift the min and max value
    var shiftArray = isPBMarkingTask();
    var isPBTask = shiftArray[0];
    var doShift = shiftArray[1];

    if (isPBTask == true) {
        max = max / 2;
    }
    if (doShift == true) {
        min = max;
        max = (2 * max);
    }

    var numMarked = getHowManyMarked(min, max, widgetName);
    var alertMsg = "";

    if (min_to_mark > 0 && numMarked < min_to_mark) {
        returnValue = false;
        if (max_to_mark == -1) {
            alertMsg = minErrMsg;
        } else {
            alertMsg = minMaxErrMsg;
        }
    } else if (max_to_mark > 0 && numMarked > max_to_mark) {
        returnValue = false;
        if (min_to_mark == -1) {
            alertMsg = maxErrMsg;
        } else {
            alertMsg = minMaxErrMsg;
        }
    }

    if (alertMsg != "") {
        alert(alertMsg);
    }

    return returnValue;
}

bpProcessKeyboardPress = function(e, keyID) {
    if (e.which == keyID) {
        if (didShowHide == false) {
            document.getElementById("halfwaySubmitButton").click();
        } else {
            document.getElementById("submitButton").click();
        }
    }
}
