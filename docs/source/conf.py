# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

import re
import os
import shutil
import sys
import logging

# Setup logger
logging.basicConfig(format="[%(levelname)s] : %(message)s", level=logging.INFO)

# Path setup
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
    "myst_parser",
]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# If not run as root, then exclude api doc generation
if os.geteuid() != 0:
    exclude_patterns.append("api")
    logging.warning(
        "Not generating API docs. If API docs are needed,"
        " then run the command with sudo."
    )

# Options for HTML output

html_title = "NeST docs"

html_theme = "furo"

html_static_path = ["_static"]

html_css_files = [
    "css/versions.css",
    "css/general.css",
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

html_logo = "assets/NeST_Logo.png"

html_theme_options = {
    "sidebar_hide_name": True,
}

# Options for sphinx multiversion
# Check https://holzhaus.github.io/sphinx-multiversion/master/configuration.html#
# to know more about the below options

smv_tag_whitelist = r"^.*$"
smv_remote_whitelist = r"^(origin)$"
smv_branch_whitelist = "master"
smv_released_pattern = r"^tags/.*$"

# The below paths are relative to docs/ folder
NeST_EXAMPLES_PATH = "../examples"
DOCS_EXAMPLES_PATH = "source/user/examples"


def insert_example_program_source_code(input):
    """
    Insert the source code of example programs.
    """
    # The sphinx myST code snippet to be inserted
    # in place of "<!-- #DOCS_INCLUDE: <example-program> -->""
    example_program_include_snippet = (
        r"{download}`Source code <\1>`\n"
        r"```{literalinclude} \1\n"
        r"---\n"
        r"language: python\n"
        r"linenos:\n"
        r"---\n"
        r"```\n"
    )

    return re.sub(
        r"<!-- #DOCS_INCLUDE: (.*) -->", example_program_include_snippet, input
    )


def uncomment_docs_content(input):
    """
    Markdown comments with content specific to docs
    are uncommented here based on regex matching.
    """
    # TODO: The below code logic doesn't cover all cases.
    # It's intentionally hacky, and should be fine for our case.

    temp_output = re.sub(r"<!--\n#BEGIN_DOCS", "", input)
    return re.sub(r"#END_DOCS\n-->", "", temp_output)


def replace_markdown_emojis(input):
    """
    Replace some selected markdown emojis with relevant
    unicode characters.
    """
    # Map of selected emojis
    emoji_map = {
        ":white_check_mark:": "✅",
        ":x:": "❌",
    }

    output = input

    # For loop is inefficient (multiple pass), but it is ok for a few emojis
    for text_emoji, unicode_emoji in emoji_map.items():
        output = re.sub(text_emoji, unicode_emoji, output)

    return output


def preprocess_markdown_content(input):
    """
    Preprocess markdown file contents:

    1. Insert example program code.
    2. Uncomment docs website specific commands.
    3. Find and replace emojis used in markdown.
    """
    temp_output1 = insert_example_program_source_code(input)
    temp_output2 = uncomment_docs_content(temp_output1)
    temp_output3 = replace_markdown_emojis(temp_output2)
    return temp_output3


def builder_inited(app):
    """
    This function is called before Sphinx build starts.

    Here we copy the NeST examples into source/user/examples
    and uncomment the docs specific content in markdown.
    """
    shutil.copytree(NeST_EXAMPLES_PATH, DOCS_EXAMPLES_PATH, dirs_exist_ok=True)
    logging.info("Copied NeST examples into %s", DOCS_EXAMPLES_PATH)

    logging.info("Modifying example README files...")
    for subdir, dirs, files in os.walk(DOCS_EXAMPLES_PATH):
        for file in files:
            if file.endswith(".md"):
                file_name = f"{subdir}/{file}"
                with open(file_name, "r") as f:
                    input = f.read()
                output = preprocess_markdown_content(input)
                with open(file_name, "w") as f:
                    f.write(output)
                logging.info("Preprocessed markdown file %s", file_name)


def build_finished(app, exception):
    """
    This function is called after sphinx build completes.

    The example programs copied to source/user/examples are
    cleaned up.
    """
    shutil.rmtree(DOCS_EXAMPLES_PATH)
    logging.info("Cleaned up %s", DOCS_EXAMPLES_PATH)


def setup(app):
    # Register callbacks with sphinx events
    app.connect("builder-inited", builder_inited)
    app.connect("build-finished", build_finished)
