# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

""" Util functions """

import importlib

from .exec import exec_subprocess


def is_dependency_installed(tool):
    """
    util to check if a tool is installed

    Parameters
    ----------
    tool : str
        tool to check

    Returns
    -------
    bool
        true if the `tool` is installed

    """
    return_code = exec_subprocess(f"type {tool}", shell=True)
    return return_code == 0


def is_package_installed(package):
    """
    Utility function to check if a python package is installed.
    This is done using importlib.

    Parameters
    ----------
    package : str
        package name to check for

    Returns
    -------
    bool
        true if the `package` is installed
    """
    is_pkg_present = False

    # Use importlib to find if the package exists
    spec = importlib.util.find_spec(package)

    # If package exists, return True
    if spec is not None:
        is_pkg_present = True

    return is_pkg_present
