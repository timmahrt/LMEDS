
---------
LMEDS
---------

.. image:: https://travis-ci.org/timmahrt/LMEDS.svg?branch=master
    :target: https://travis-ci.org/timmahrt/LMEDS

.. image:: https://coveralls.io/repos/github/timmahrt/LMEDS/badge.svg?branch=master
    :target: https://coveralls.io/github/timmahrt/LMEDS?branch=master

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?
   :target: http://opensource.org/licenses/MIT

A web platform for collecting text annotation and experiment data online.

LMEDS was originally developed for conducting Rapid Prosody Transcription annotations
over the internet.  Since then it has been extended for doing a number of
different types of perceptual experiments (memory tasks, AXB-type tasks, etc.).

.. sectnum::
.. contents::

Major revisions
================

Ver 2.2 (Dec 15, 2015)

- Added support for python 3.x (tested on 3.5)

Ver 2.1 (Sep 18, 2015)

- Replaced the many AXB page classes with one flexible audio_choice class

Ver 2.0 (Aug 12, 2015)

- First public release.  

- Inclusion of user script utilities.

- Numerous bugfixes and stability improvements (audio is significantly less error prone).  

- Offline server for running experiments locally.

- Companion website.


Ver 1.5 (May 19, 2014)

- Object oriented refactor

- Numerous bugfix and stability improvements.


Ver 1.0 (December 04, 2013)

- First stable release


Requirements
==============

``Python 2.7.*`` or above

``Python 3.5.*`` or above


Usage
=========

LMEDS needs to be installed on a server and probably needs to be done by someone
with a technical background. Once installed, experiments can be built with no 
programming experience.  Please see the document LMEDS_manual.pdf for instructions 
on installation and use.


Installation
================

Please see the manual for instructions on installing LMEDS on a server, running
LMEDS on a local computer (no server required), or for using the included user scripts.


Citing LMEDS
===============

If you use LMEDS in your research, please cite it like so:

Tim Mahrt. LMEDS: Language markup and experimental design software.
https://github.com/timmahrt/LMEDS, 2016.


Acknowledgements
================

Development of LMEDS was supported by NSF grant **BCS 12-51343**
to Jennifer Cole, José Hualde, and Caroline Smith.
