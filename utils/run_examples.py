# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

import os
from pathlib import Path
import pytest
import subprocess
import json

UTILS_DIR = Path(os.path.abspath(__file__)).parent
ROOT_DIR = UTILS_DIR.parent
EXAMPLES_DIR = ROOT_DIR / "examples"

# Create a directory for all example dumps
# and cd into that directory
EXAMPLES_DUMP_DIR = ROOT_DIR / "examples_dump"
Path(EXAMPLES_DUMP_DIR).mkdir(exist_ok=True)
os.chdir(EXAMPLES_DUMP_DIR)

# Load default command line args for some examples
with open(UTILS_DIR / "default_examples_args.json") as json_file:
    ARGS = json.load(json_file)

# Helper methods


def run_example(path):
    """
    Run example from the given `path`
    """
    cmd = ["python3", path] + get_args(path)
    return_code = subprocess.call(cmd)
    return return_code


def get_args(path):
    """
    Get command line arguments for examples, if needed.
    If not required, return an empty list.
    """
    for key, val in ARGS.items():
        if path.endswith(key):
            return val
    return []


# Lists contains all example program paths
# abs_example_paths contains absolute paths of all examples
# rel_example_paths contains relateive paths of all examples
abs_example_paths = []
rel_example_paths = []

for root, subdirs, files in os.walk(EXAMPLES_DIR):
    for f in files:
        path = os.path.join(root, f)
        if path.endswith(".py"):
            abs_example_paths.append(path)
            rel_example_paths.append(os.path.relpath(path, EXAMPLES_DIR))

# Main test method. The below command calls this function
# $ pytest -o python_files="utils/run_examples.py"
# (Note, the above command should be run in root folder of repo)
@pytest.mark.parametrize("example_path", abs_example_paths, ids=rel_example_paths)
def test_example(example_path):
    status_code = run_example(example_path)
    assert status_code == 0, f"{example_path} failed!"
