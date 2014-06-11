#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app
@app.route('/app/cgi-bin/rpt_demo.cgi')
def run_experiment:
    return 'Hello you made it!'

import experiment_runner
experiment_runner.runExperiment("demo", "/cgi-bin/sequence.txt", "/cgi-bin/english.txt", disableRefresh=False)    
    
