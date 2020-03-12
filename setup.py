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

INSTALL_REQUIREMENTS = ["pandas", "xarray"]

setuptools.setup(name='tvb-scripts',
                 version=VERSION,
                 packages=setuptools.find_packages(),
                 include_package_data=True,
                 install_requires=INSTALL_REQUIREMENTS,
                 description='A package with helper functions, '
                             'some additional datatypes, '
                             'plotting functions, '
                             'a Timeseries model and service, '
                             'io module to and from TVB and h5 files'
                             'and a virtual_head model and services for TVB Structural data, '
                             'for more efficient TVB scripting.',
                 license="GPL v3",
                 author="TVB Team",
                 author_email='tvb.admin@thevirtualbrain.org',
                 url='http://www.thevirtualbrain.org',
                 # download_url='https://github.com/the-virtual-brain/tvb-scripts',
                 keywords='tvb brain simulator neuroscience human animal neuronal dynamics models delay data')

shutil.rmtree('tvb_scripts.egg-info', True)
