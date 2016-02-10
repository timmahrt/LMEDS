#!/usr/bin/env python
'''
This is the lmeds server.  Launch this from a terminal with the command line
(cmd on windows; terminal, etc on os x or linux) via
python lmeds_local_server.py

To run an experiment session visit:
http://localhost:8123/cgi-bin/<<name of your experiment>>.cgi

On windows, you must rename the file <<name of your experiment>>.py
and visit:
http://localhost:8123/cgi-bin/<<name of your experiment>>.py
'''

import os
from os.path import join

try:
    from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
except ImportError:
    from http.server import BaseHTTPRequestHandler,HTTPServer,CGIHTTPRequestHandler
else:
    from CGIHTTPServer import CGIHTTPRequestHandler

lmedsPath = os.path.dirname(os.path.realpath(__file__))
os.chdir(lmedsPath)

handler = CGIHTTPRequestHandler
handler.cgi_directories = ['/cgi-bin']
server = HTTPServer(('127.0.0.1', 8123), handler)

print("\nServer running!\n\n"
      "CLOSING THIS WINDOW WILL PREVENT PARTICIPANTS FROM SAVING DATA "
      "AND CONTINUING EXPERIMENT!!!\n\n" 
      "To run an experiment session on this computer visit:\n"
      "http://127.0.0.1:8123/cgi-bin/<<name of your experiment>>.cgi\n\n"
      "(or on windows, rename the file to <<name of your experiment>>.py and visit:\n"
      "http://127.0.0.1:8123/cgi-bin/<<name of your experiment>>.py\n\n"
      "When all data collection is complete, you may safetly close this window")
server.serve_forever()