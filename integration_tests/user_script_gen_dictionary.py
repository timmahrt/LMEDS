'''
Created on Apr 29, 2016

@author: Tim
'''

import base_demo
from lmeds.user_scripts import generate_language_dictionary

generate_language_dictionary.generateLanguageDictionary("update", "LMEDS_DEMO",
                                                        "sequence.txt",
                                                        "english.txt"
                                                        )
