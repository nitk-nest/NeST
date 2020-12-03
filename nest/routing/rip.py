# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Class to handles RIP related functionalities"""

from nest.engine.quagga import run_ripd
from nest.routing.quagga_base import QuaggaBase


class Rip(QuaggaBase):
    """
    Handles RIP related functionalities for Quagga.
    Refer to `QuaggaBase` for usage
    """

    def __init__(self, router_ns_id, interfaces, conf_dir):
        super().__init__(router_ns_id, interfaces, 'ripd', conf_dir)

    def add_rip(self):
        """
        Add command to enable RIP on router to config file
        """
        self.add_to_config('router rip')

    def add_version(self, version):
        """
        Add version command to config file

        Parameters
        ----------
        version : str
            RIP version. Recommended is v2
        """
        self.add_to_config(f' version {version}')

    def add_network(self, network):
        """
        Add command for subnet or interface to run RIP on to config file

        Parameters
        ----------
        network : str
            subnet or interface to run RIP on
        """
        self.add_to_config(f' network {network}')

    def create_basic_config(self):
        """
        Creates a file with basic configuration for RIP.
        Use base `add_to_config` directly for more complex configurations
        """
        self.add_rip()
        self.add_version(2)
        for interface in self.interfaces:
            self.add_network(interface.id)

        self.create_config()

    def run(self):
        """
        Runs the ripd command
        """
        run_ripd(self.router_ns_id, self.conf_file, self.pid_file)
