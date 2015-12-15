'''
Created on Aug 4, 2015

@author: tmahrt
'''

import sys
import argparse


class InteractiveModeException(Exception):
    
    def __str__(self):
        return "This exception isn't meant to be printed."
    

def runScriptLogic(parser):
    if len(sys.argv) > 1:
        cmdArgs = parser.parse_args()

    else:

        # Python 2-to-3 compatibility hack
        try:
            inputFunc = raw_input  # Python 2.x
        except NameError:
            inputFunc = input  # Python 3.x
        
        # If the user doesn't want to run interactive mode, show the
        # command-line options
        # Interactive mode allows the script to be run from IDEs like IDLE
        doInteractive = inputFunc("No arguments given. "
                                  "Try interactive mode (y/n)?\n")
        if doInteractive.lower() == 'n':
            sys.argv.append("-h")
            cmdArgs = parser.parse_args()
        else:
            raise InteractiveModeException()

    return cmdArgs
