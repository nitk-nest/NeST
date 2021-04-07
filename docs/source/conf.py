# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

# Path setup

import os
import sys

sys.path.insert(0, os.path.abspath("../"))

# Get version
ver = {}
with open("../../nest/version.py") as fp:
    exec(fp.read(), ver)

# Project information

project = "NeST"
copyright = "2019-2021 NITK Surathkal"
author = "Shanthanu S Rai, Narayan G, Dhanasekhar M, Leslie Monis, Mohit P. Tahiliani"
release = ver["__version__"]

# General configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",
    "sphinx_multiversion",
]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Options for HTML output

html_theme = "furo"

html_static_path = ["_static"]

html_css_files = [
    "css/versions.css",
]

html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "sidebar/ethical-ads.html",
        "sidebar/scroll-end.html",
        "sidebar/versions.html",
    ]
}

# Options for sphinx multiversion
# Check https://holzhaus.github.io/sphinx-multiversion/master/configuration.html#
# to know more about the below options

smv_tag_whitelist = r"^.*$"
smv_remote_whitelist = r"^(origin)$"
smv_branch_whitelist = r"$^"  # No branch should be added
