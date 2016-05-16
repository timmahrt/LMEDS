'''
Created on Apr 29, 2016

@author: tmahrt

Runs integration tests

The examples were all written as scripts.  They weren't meant to be 
imported or run from other code.  So here, the integration test is just
importing the scripts, which causes them to execute.  If the code completes
with no errors, then the code is at least able to complete.

Testing whether or not the code actually did what it is supposed to is
another issue and will require some refactoring.
'''

import unittest
import os
import sys

cwd = os.path.dirname(os.path.realpath(__file__))
_root = os.path.split(cwd)[0]
sys.path.append(_root)
os.chdir(_root)

class UserScriptIntegrationTests3(unittest.TestCase):
    """Integration tests"""
    def test_post_process(self):
        """Running 'get_duration_demo'"""
        import user_script_post_process


if __name__ == '__main__':
    unittest.main()
