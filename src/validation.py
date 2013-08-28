#!/usr/local/bin/python
# -*- coding: utf-8 -*-

#from output import typeList, pgList

import loader

choice = """<input type="radio" name="radio">"""
img = """<img src="data/%s">"""
txtBox = """<input type="text" name="%s" value=""/>"""
radioButton = """<input type="radio" name="radio" value="%s">"""



radioboxTemplate = 'checkBoxValidate(y["%s"])'
textboxTemplate = 'textBoxValidate(y["%s"])'
textBoxTemplateFilter = 'textBoxFilter(y["%s"])'
radioboxTemplateFilter = 'choiceFilter(y["%s"])'

templateDict = {"radio":radioboxTemplate,
                "check":radioboxTemplate,
                "box":textboxTemplate,
                "boxFilter":textBoxTemplateFilter,
                "radioFilter":radioboxTemplateFilter,
                }

loginValidation = """
var y=document.forms["languageSurvey"];

if (textBoxValidate(y["user_name_init"])==1)
  {
  alert("%s");
  return false;
  }
  return true;
"""

template = """
var y=document.forms["languageSurvey"];
if (%s==true)
  {
  alert("Warning: Some fields left blank");
  return false;
  }
  return true;
"""

consentValidation = """
var y=document.forms["languageSurvey"];
if (checkBoxValidate(y["radio"])==true)
  {
  alert("%s");
  return false;
  }
  return true;
"""

# Can be used for axb or ab page validation
abValidation = """
var y=document.forms["languageSurvey"];
if (checkBoxValidate(y["axb"])==true)
  {
  alert("%s");
  return false;
  }
  return true;
"""


skipValidateList = []
checkList = [43,44,45,46,47]

def getValidationForPage(testType):
    
    if testType == 'login' or testType == 'login_bad_user_name':
        retPage = loginValidation % loader.getText('error blank name')
    elif testType == 'consent':
        retPage = consentValidation % loader.getText('error consent or dissent')
    elif testType == 'axb' or testType == 'ab':
        retPage = abValidation % loader.getText('error select a or b')
    else: 
        retPage = template % "||".join([])
        
    return retPage
        

