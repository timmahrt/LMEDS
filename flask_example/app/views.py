from app import app
from flask import redirect
import os.path

@app.route('/')
@app.route('/index')
def index():
    from app.lmeds import experiment_runner

    retval = experiment_runner.runExperiment("gails_test", "/home/gail/Senior_Project/lmeds/flask_example/app/tests/sequence.txt",\
     "/home/gail/Senior_Project/lmeds/flask_example/app/tests/english.txt", disableRefresh=False)

    outfile = open('out.txt', 'w')
    outfile.write(retval)

    return retval; 