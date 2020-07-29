# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""
Base class for other runners
"""

import tempfile
from ...engine import exec_exp_commands


class Runner:
    """
    Base class for other runners

    Attributes
    ----------
    out : File
        temporary file to hold the stats
    err : File
        temporary file to hold any errors
    """

    def __init__(self):
        self.out = tempfile.TemporaryFile()
        self.err = tempfile.TemporaryFile()

    def run(self, command):
        """
        Runs the `command` and stores stdout or stderr
        """
        return_code = exec_exp_commands(
            command, stdout=self.out, stderr=self.err)
        if return_code != 0:
            self.print_error()

    def print_error(self):
        """
        Method to print error from `self.err`.
        Should be overriden by base class
        """
        print('Unknown error occured')

    def clean_up(self):
        """
        Closes the temp files created
        """
        self.out.close()
        self.err.close()
