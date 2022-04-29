#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

with open('nose2_test_timer/__init__.py') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='nose2-test-timer',
    version=version,
    description='A timer plugin for nose2',
    long_description=long_description,
    author='Kaichia Chen',
    author_email='kaichiaboy@gmail.com',
    url='https://github.com/kaichiachen/nose2-test-timer',
    packages=['nose2_test_timer', ],
    install_requires=[
        'nose2',
        'colorama'
    ],
    license='MIT',
    entry_points={
        'nose.plugins.0.0.3': [
            'nose2_test_timer = nose2_test_timer.plugin:TimerPlugin',
        ]
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Testing',
        'Environment :: Console',
    ],
)
