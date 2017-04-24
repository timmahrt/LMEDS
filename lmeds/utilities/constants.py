'''
Created on Mar 28, 2013

@author: timmahrt

DON'T CHANGE UNLESS YOU KNOW WHAT YOU'RE DOING
-- please use this page as a reference to know where to put things
'''

import types
from os.path import join

# EDITING THESE ONLY MODIFIES METADATA AND WILL NOT IMPAIR LMEDS
softwareLogo = '<img src="../imgs/lmeds_logo.png"><br />'
softwareName = "LMEDS: Language Markup and Experimental Design Software"

# Insert url here of LMEDS.  This is used by a few
# files (just .ico?) so not filling this in is not hugely problematic
rootURL = ""


# EDITING THE BELOW MIGHT PREVENT LMEDS FROM FUNCTIONING

rootDir = ".."

#
htmlDir = join(rootDir, "html")
htmlSnippetsDir = join(htmlDir, "snippets")
instructDir = join(htmlDir, "instructions")

# Python 2 str, to unicode
try:
    list = types.ListType  # Python 2.x
except AttributeError:
    list = list  # Python 3.x
