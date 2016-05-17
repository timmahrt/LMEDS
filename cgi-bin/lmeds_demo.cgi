#!/usr/bin/env python
# -*- coding: utf-8 -*-

import experiment_runner
experiment_runner.runExperiment("lmeds_demo",
                                "sequence.txt",
                                "english.txt",
                                disableRefresh=False,
                                audioExtList=[".ogg", ".mp3"],
                                videoExtList=[".ogg", ".mp4"],
                                allowUtilityScripts=True,
                                allowUsersToRelogin=True)
    