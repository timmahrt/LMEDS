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

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from CGIHTTPServer import CGIHTTPRequestHandler

handler = CGIHTTPRequestHandler
handler.cgi_directories = ['/cgi-bin']
server = HTTPServer(('localhost', 8123), handler)

print("\nServer running!\n\n"
      "CLOSING THIS WINDOW WILL PREVENT PARTICIPANTS FROM SAVING DATA "
      "AND CONTINUING EXPERIMENT!!!\n\n" 
      "To run an experiment session on this computer visit:\n"
      "http://localhost:8123/cgi-bin/<<name of your experiment>>.cgi\n\n"
      "(or on windows, rename the file to <<name of your experiment>>.py and visit:\n"
      "http://localhost:8123/cgi-bin/<<name of your experiment>>.py\n\n"
      "When all data collection is complete, you may safetly close this window")
server.serve_forever()