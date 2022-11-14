# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

import json
import os
from pathlib import Path
import pytest
from subprocess import PIPE, run
import sys

UTILS_DIR = Path(os.path.abspath(__file__)).parent
ROOT_DIR = UTILS_DIR.parent
EXAMPLES_DIR = ROOT_DIR / "examples"

EXAMPLES_TO_SKIP = ["mpls-ldp-ce-pe-p-routers-multi-address.py"]

# Create a directory for all example dumps
# and cd into that directory
EXAMPLES_DUMP_DIR = ROOT_DIR / "examples_dump"
Path(EXAMPLES_DUMP_DIR).mkdir(exist_ok=True)
os.chdir(EXAMPLES_DUMP_DIR)

# Load default command line args for some examples
with open(UTILS_DIR / "default_examples_args.json") as default_examples_args:
    ARGS = json.load(default_examples_args)

# Load standard input for some examples
with open(UTILS_DIR / "examples_stdin.json") as examples_stdin:
    INPUT = json.load(examples_stdin)


def run_example(path):
    """
    Run example from the given `path`
    """
    cmd = ["coverage", "run", "--rcfile", UTILS_DIR / ".coveragerc", path] + get_args(
        path
    )
    result = run(cmd, input=get_input(path), stdout=PIPE, stderr=PIPE)
    return result


def get_args(path):
    """
    Get command line arguments for examples, if needed.
    If not required, return an empty list.
    """
    for key, val in ARGS.items():
        if path.endswith(key):
            return val
    return []


def get_input(path):
    """
    Get the standard input for example, if needed.
    If not required, return `None`.
    """
    for key, val in INPUT.items():
        if path.endswith(key):
            return val.encode()
    return None


# Lists contains all example program paths
# abs_example_paths contains absolute paths of all examples
# rel_example_paths contains relateive paths of all examples
abs_example_paths = []
rel_example_paths = []

for root, subdirs, files in os.walk(EXAMPLES_DIR):
    for f in files:
        path = os.path.join(root, f)
        if path.endswith(".py") and (f not in EXAMPLES_TO_SKIP):
            abs_example_paths.append(path)
            rel_example_paths.append(os.path.relpath(path, EXAMPLES_DIR))


# Main test method. The below command calls this function
# $ pytest -o python_files="utils/run_examples.py"
# (Note, the above command should be run in root folder of repo)
@pytest.mark.parametrize("example_path", abs_example_paths, ids=rel_example_paths)
def test_example(example_path):
    # Run example
    result = run_example(example_path)
    stdout = result.stdout.decode()
    stderr = result.stderr.decode()
    return_code = result.returncode

    # Print stdout, stderr
    print(stdout, file=sys.stdout)
    print(stderr, file=sys.stderr)

    # Fail test if example exited with non-zero status
    assert return_code == 0, (
        f"{example_path} exited with non-zero status code (return_code = {return_code}). "
        f"Please check the example output in logs."
    )

    # Fail test if example output contained any error messages or failures
    # NOTE: Add phrases in lower cases only
    PHRASES_INDICATING_FAILURE = [
        "error",
        "fail",
        "traceback",
        "100% packet loss",  # Output when ping fails
    ]

    assert not any(
        phrase in (stdout + "\n" + stderr).lower()
        for phrase in PHRASES_INDICATING_FAILURE
    ), f"{example_path} stdout/stderr indicate failure. Please check the example output in logs."
