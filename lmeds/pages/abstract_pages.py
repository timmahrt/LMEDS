'''
Created on Feb 27, 2014

@author: tmahrt

Pages within here are both abstract (not to be instantiated) and general
to all types of pages.  Abstract pages specific to certain tests should
go in a more specific file.
'''

from os.path import join

from lmeds import html

abValidation = """
var y=document.forms["languageSurvey"];
if (checkBoxValidate(y["axb"])==true)
  {
  alert("%s");
  return false;
  }
  return true;
"""

audioTextKeys = ["error_must_play_audio_at_least", "error_must_play_audio",
                 'play_button']

class KeyNotInFormError(Exception):
    
    def __init__(self, key):
        super(KeyNotInFormError, self).__init__()
        self.key = key
        
    def __str__(self):
        errStr = "Attempted to get testoutput but key '%s' not in form."
        return errStr % self.key


def getoutput(key, form, appendDefault=False):
    '''
    
    Output from the cgi form is the name of the indices that were marked
    positive. Here we use the convention that checkboxes are ordered and
    named as such (e.g. "1", "2", "3", etc.).
    
    This code converts this list into the full list of checked and unchecked
    boxes, where the index of the item in the row contains the value of the
    corresponding checkbox
    e.g. for 'Tom saw Mary' where each word can be selected by the user,
    the sequence [0, 0, 1] would indicate that 'Mary' was selected and 'Tom'
    and 'saw' were not.
    '''
    numItems = int(form.getvalue('num_items'))
    
    # Prevents data from being lost (if we're expecting something from
    #    being there and its not) otherwise, LMEDS will silently continue
    #    as if nothing was wrong.  This doesn't alert the user in any useful
    #    way but at least it alerts them that something is wrong
    if numItems > 0:
        if key not in form:
            raise KeyNotInFormError(key)
    
    # Contains index of all of the positively marked items
    # (ignores unmarked items)
    outputList = form.getlist(key)

    # Assume all items unmarked
    retList = ["0" for i in xrange(numItems)]
    
    # Mark positively marked items
    for i in outputList:
        retList[int(i)] = "1"
        
    if appendDefault:
        if all([char == '0' for char in retList]):
            retList.append('1')
        else:
            retList.append('0')
    
    return ",".join(retList)


class NotDefinedError(Exception):
    
    def __str__(self):
        return "Variable not defined in child class"
    

class NoCorrectResponseError(Exception):
    
    def __str__(self):
        return "This pageClass does not have right or wrong answers"
    
    
def checkResponseCorrectByIndex(responseList, correctResponseIndex):
    '''For pages that have a single correct answer among a list of options'''
    return responseList.index('1') == correctResponseIndex


class AbstractPage(object):
    '''
    All pages derive from this page directly or indirectly
    '''
    sequenceName = None
    
    def __init__(self, webSurvey, *args, **kargs):
        super(AbstractPage, self).__init__(*args, **kargs)
        self.webSurvey = webSurvey
        
        # These are variables that all pages can define
        
        # e.g. [('widget', 'myWidget'), ('timeout', 1.0)]
        self.nonstandardSubmitProcessList = []
        
        self.submitProcessButtonFlag = True
    
        # Page text strings are stored here
        self.textDict = {}
    
        # Variables that all pages need to define
        self.numAudioButtons = None
        self.processSubmitList = None
    
    def checkResponseCorrect(self, responseList, correctResponse):
        raise NotImplementedError("Should have implemented this")
        
    def getValidation(self):
        raise NotImplementedError("Should have implemented this")
    
    def getHTML(self):
        raise NotImplementedError("Should have implemented this")
    
    def getNumOutputs(self):
        raise NotImplementedError("Should have implemented this")
    
    def getOutput(self, form):
        
        if self.sequenceName is None:
            raise NotDefinedError()
        
        return getoutput(self.sequenceName, form)
    
    def getNumAudioButtons(self):
        if self.numAudioButtons is None:
            raise NotDefinedError()
        
        return self.numAudioButtons
    
    def getProcessSubmitFunctions(self):
        '''
        Returns html-formatted functions that should be run after 'submit'
        
        Current possible keys (need to put these somewhere):
        "verifyAudioPlayed"# Ensure the subject has listened to all audio files
        "validateForm" # Ensure all required forms have been filled out
        '''
        
        if self.processSubmitList is None:
            raise NotDefinedError()
        
        htmlList = []
        for func in self.processSubmitList:
            htmlList.append("returnValue = returnValue && %s();" % func)
    
        htmlTxt = "\n".join(htmlList)
    
        return html.processSubmitHTML % htmlTxt
        
        
class NonRecordingPage(AbstractPage):
    '''
    For pages that don't record any data
    '''
    
    def checkResponseCorrect(self, responseList, correctResponse):
        raise NoCorrectResponseError()
    
    def getOutput(self, form):
        
        return []
    
    def getNumOutputs(self):
        
        return 0


class NonValidatingPage(NonRecordingPage):
    '''
    For pages that don't require validation
    '''
    def getValidation(self):
        template = ""
        
        return template


class FileDoesNotExist(BaseException):
    
    def __init__(self, path, name):
        self.path = path
        self.name = name
        
    def __str__(self):
        return "File '%s' does not exist" % join(self.path, self.name)
