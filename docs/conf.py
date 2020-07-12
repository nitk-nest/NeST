# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# Path setup

import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import sphinx_rtd_theme

# Project information

project = 'NeST'
copyright = '2020, NITK'
author = 'Shanthanu S Rai, Narayan G, Dhanasekhar M, Leslie Monis, Mohit P. Tahiliani'
release = '0.0.1'

# General configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme'
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Options for HTML output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']