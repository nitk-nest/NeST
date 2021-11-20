# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

import os
import sys
from pathlib import Path
import subprocess
import json

UTILS_DIR = Path(__file__).parent
ROOT_DIR = UTILS_DIR.parent
EXAMPLES_DIR = ROOT_DIR / "examples"

with open(UTILS_DIR / "default_examples_args.json") as json_file:
    ARGS = json.load(json_file)


def run_example(path):
    """
    Run example from the given `path`
    """
    cmd = ["python3", path] + get_args(path)
    print(f"==> Command run: {' '.join(cmd)}\n")

    print("==> Output\n")
    return_code = subprocess.call(cmd)
    print("\n==> End of Output\n")

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


def get_default_examples_args(json_file_path):
    """
    Get default example command line args from JSON file.
    """
    with open(json_file_path) as json_file:
        default_example_args = json.load(json_file)
        return default_example_args


if __name__ == "__main__":
    # Create a directory for all example dumps
    # and cd into that directory
    EXAMPLES_DUMP_DIR = ROOT_DIR / "examples_dump"
    Path(EXAMPLES_DUMP_DIR).mkdir(exist_ok=True)
    os.chdir(EXAMPLES_DUMP_DIR)

    # Run all examples sequentially and record any
    # failed example runs
    failed_example_runs = []
    for root, subdirs, files in os.walk(EXAMPLES_DIR):
        for f in files:
            path = os.path.join(root, f)
            if path.endswith(".py"):
                return_code = run_example(path)
                if return_code != 0:
                    failed_example_runs.append(path)

    # Report failed example runs, if any
    if len(failed_example_runs) != 0:
        print("==> The below example runs failed:")
        for example in failed_example_runs:
            print(f"==> {example}")
        sys.exit(1)
