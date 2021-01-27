# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

""" Util functions """

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
