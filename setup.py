# -*- coding: utf-8 -*-
#
#
#

"""
Install TVB Head package for developers.

Execute:
    python setup.py install/develop

"""

import shutil
import setuptools


VERSION = "1.0.0"


setuptools.setup(name='tvb-scripts',
                 version=VERSION,
                 packages=setuptools.find_packages(),
                 include_package_data=True,
                 description='A package with helper functions (tvb-utils), '
                             'plotting functions (tvb-plot), '
                             'a Timeseries4D model and service (tvb-timeseries), '
                             'io module (tvb-io) to and from TVB and h5 files'
                             'and a tvb-head model and services for TVB Structural data, '
                             'for more efficient TVB scripting.',
                 license="GPL v3",
                 author="TVB Team",
                 author_email='tvb.admin@thevirtualbrain.org',
                 url='http://www.thevirtualbrain.org',
                 # download_url='https://github.com/the-virtual-brain/tvb-subject',
                 keywords='tvb brain simulator neuroscience human animal neuronal dynamics models delay data')

shutil.rmtree('tvb_scripts.egg-info', True)
