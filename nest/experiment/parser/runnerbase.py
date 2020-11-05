# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""
Base class for other runners
"""

import tempfile
import logging
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
    start_time : num
            time at which netperf is to run
    run_time : num
        total time to run netperf for
    """

    def __init__(self, start_time, run_time):
        self.out = tempfile.TemporaryFile()
        self.err = tempfile.TemporaryFile()

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        self.start_time = start_time
        self.run_time = run_time

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
        Should be overridden by base class
        """
        self.logger.error('Unknown error occurred')

    def get_meta_item(self):
        """
        Return the meta item for the given flow.
        This "meta" information is required by plotter.
        """
        meta_item = {
            'meta': True,
            'start_time': str(self.start_time),
            'stop_time': str(self.start_time + self.run_time)
        }
        return meta_item

    def __del__(self):
        """
        Close the temp files created
        """
        self.out.close()
        self.err.close()
