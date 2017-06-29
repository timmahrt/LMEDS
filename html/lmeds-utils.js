
var Timer = function() {
    this.start = new Date().getTime();
    this.stop = null;
}

Timer.prototype.calcDuration = function() {
    this.end = new Date().getTime()
    var time = this.end - this.start;

    var seconds = Math.floor(time / 100) / 10;
    var minutes = Math.floor(seconds / 60);
    seconds = seconds - (minutes * 60);
    if (Math.round(seconds) == seconds) {
        seconds += '.0';
    }
    var param1 = minutes.toString();
    var param2 = Number(seconds).toFixed(1);

    return param1 + ":" + param2;
}

function isSupportedBrowser() {
    if (!!document.createElement('audio').canPlayType == false) {
        document.getElementById("submit").disabled = true;
        document.getElementById("unsupported_warning").style.display = 'block';
    }
}

function countUnique(someList) {
    var uniqueList = []
    for (i = 0; i < someList.length; i++) {
        addItem = 1;
        for (j = 0; j < uniqueList.length; j++) {
            addItem &= someList[i] != uniqueList[j];
        }
        if (addItem == 1) {
            uniqueList.push(someList[i]);
        }
    }
    return uniqueList.length;
}
