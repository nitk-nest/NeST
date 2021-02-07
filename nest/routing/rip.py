# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Class to handles RIP related functionalities"""

from functools import partial
from nest.engine.dynamic_routing import run_ripd
from nest.routing.route_daemons import RoutingDaemonBase


class Rip(RoutingDaemonBase):
    """
    Handles RIP related functionalities.
    Refer to `DaemonBase` for usage
    """

    def __init__(self, router_ns_id, interfaces, conf_dir, **kwargs):
        super().__init__(router_ns_id, interfaces, "ripd", conf_dir, **kwargs)

    def add_rip(self):
        """
        Add command to enable RIP on router to config file
        """
        if self.ipv6:
            self.add_to_config("router ripng")
        else:
            self.add_to_config("router rip")

    def add_network(self, network):
        """
        Add command for subnet or interface to run RIP on to config file

        Parameters
        ----------
        network : str
            subnet or interface to run RIP on
        """
        self.add_to_config(f" network {network}")

    def create_basic_config(self):
        """
        Creates a file with basic configuration for RIP.
        Use base `add_to_config` directly for more complex configurations
        """
        self.add_rip()
        for interface in self.interfaces:
            self.add_network(interface.id)
        if self.log_file is not None:
            self.add_to_config(f"log file {self.log_file}")

    def run(self):
        """
        Runs the ripd command
        """
        super().run(
            engine_func=partial(
                run_ripd, self.router_ns_id, self.conf_file, self.pid_file, self.ipv6
            )
        )
