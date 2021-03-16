# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""
Base class for other runners
"""

import tempfile
import logging
from nest.topology import Address


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
            time at which utility is to run
    run_time : num
        total time for a utility to run
    destination_address : Address
        Address of the destination node for the runner
    """

    def __init__(self, start_time, run_time, destination_ip="::1"):
        """
        Parameters
        ----------
        destination_ip : str
            ip address of the destination namespace
        """
        self.out = tempfile.TemporaryFile()
        self.err = tempfile.TemporaryFile()

        self.logger = logging.getLogger(__name__)

        self.destination_address = Address(destination_ip)
        self.start_time = start_time
        self.run_time = run_time

    def run(self, engine_func):
        """
        executes the given engine function and prints error(if any)

        Parameters
        ----------
        engine_func: Function
            engine function to be called
        """
        return_code = engine_func(out=self.out, err=self.err)
        if return_code != 0:
            self.print_error()

    def print_error(self):
        """
        Method to print error from `self.err`.
        Should be overridden by base class
        """
        self.logger.error("Unknown error occurred")

    def get_meta_item(self):
        """
        Return the meta item for the given flow.
        This "meta" information is required by plotter.
        """
        meta_item = {
            "meta": True,
            "start_time": str(self.start_time),
            "stop_time": str(self.start_time + self.run_time),
        }
        return meta_item

    def __del__(self):
        """
        Close the temp files created
        """
        self.out.close()
        self.err.close()
