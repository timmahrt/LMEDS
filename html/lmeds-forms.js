
// Sets the choice box to be a null option so the user is
// forced to make a selection
function setchoiceboxes() {
    selectList = document.getElementsByTagName('select');
    for (var i = 0; i < selectList.length; i++) {
        selectBox = selectList[i];
        selectBox.selectedIndex = -1;
    }
}


// Radio Button Validation
// copyright Stephen Chapman, 15th Nov 2004,14th Sep 2005
// you may copy this function but please keep the copyright notice with it
function checkBoxValidate(choice) {
    var cnt = -1;
    for (var i = choice.length - 1; i > -1; i--) {
        if (choice[i].checked) {
            cnt = i;
            i = -1;
        }

    }
    if (cnt == -1) {
        return 1;
    }
    return 0;
}

function choiceFilter(choice) {
    if (checkBoxValidate(choice) == 1) {
        choice.value = " ";
    }
}

function textBoxFilter(box) {

    if (box.value == null || box.value == "") {
        box.value = " ";
    }
    return 0
}

function textBoxValidate(box) {
    textBoxFilter(box);
    if (box.value == null || box.value == " ") {
        return 1;
    }
    return 0;
}

function validateForm(alertTxt) {

    var y = document.forms["languageSurvey"];
    if (checkBoxValidate(y["radio"]) == true) {
        alert(alertTxt);
        return false;
    }
    return true;

}
