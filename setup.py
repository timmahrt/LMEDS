#!/usr/bin/env python
# encoding: utf-8
'''
Created on Apr 29, 2016

@author: tmahrt
'''
from distutils.core import setup
import io
setup(name='lmeds',
      version='2.5.3',
      author='Tim Mahrt',
      author_email='timmahrt@gmail.com',
      package_dir={'lmeds': 'lmeds'},
      packages=['lmeds',
                'lmeds.code_generation',
                'lmeds.lmeds_io',
                'lmeds.pages',
                'lmeds.post_process',
                'lmeds.user_scripts',
                'lmeds.utilities', ],
      package_data={'lmeds': ['html/*.html', 'html/*.css', 'html/*.js'
                              'imgs/*.png']},
      license='LICENSE',
      test_suite='nose.collector',
      tests_require=['nose'],
      description="A web platform for collecting text annotation and experiment data online",
      long_description=io.open('README.rst', 'r', encoding="utf-8").read(),
#       install_requires=[], # No requirements! # requires 'from setuptools import setup'
      )
