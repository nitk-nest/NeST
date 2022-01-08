# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""
Base class for other runners
"""

import tempfile
import logging
from nest.topology import Address
from nest.topology_map import TopologyMap


# pylint: disable=too-many-instance-attributes
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

    # pylint: disable=too-many-arguments
    def __init__(self, ns_id, start_time, run_time, destination_ip="::1", dst_ns=None):
        """
        Parameters
        ----------
        ns_id: str
            Namespace where the utility is run
        destination_ip: str
            ip address of the destination namespace
        dst_ns: str
            Optional. The namespace where the utility either sends traffic to,
            or monitors traffic that is going from `ns_id` to `dst_ns`
        """
        # pylint: disable=consider-using-with
        self.out = tempfile.TemporaryFile()
        self.err = tempfile.TemporaryFile()

        self.logger = logging.getLogger(__name__)

        self.ns_id = ns_id
        self.dst_ns = dst_ns
        self.start_time = start_time
        self.run_time = run_time
        self.destination_address = Address(destination_ip)

    def run(self, engine_func, error_string_prefix="Error"):
        """
        executes the given engine function and prints error(if any)

        Parameters
        ----------
        engine_func: Function
            engine function to be called
        """
        return_code = engine_func(out=self.out, err=self.err)
        if return_code != 0:
            self.print_error(error_string_prefix)

    def print_error(self, error_string_prefix):
        """
        Method to print error from `self.err`
        """
        self.err.seek(0)  # rewind to start of file
        error = self.err.read().decode()
        ns_name = TopologyMap.get_namespace(self.ns_id)["name"]
        self.logger.error("%s at %s. %s", error_string_prefix, ns_name, error)

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

        if self.dst_ns is not None:
            meta_item["destination_node"] = TopologyMap.get_namespace(self.dst_ns)[
                "name"
            ]

        return meta_item

    def __del__(self):
        """
        Close the temp files created
        """
        self.out.close()
        self.err.close()
