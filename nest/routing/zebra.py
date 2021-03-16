# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Class to handle zebra"""

from nest.routing.route_daemons import RoutingDaemonBase
from nest.engine.dynamic_routing import run_zebra


class Zebra(RoutingDaemonBase):
    """
    Handles zebra related functionalities.
    Refer to `DaemonBase` for usage
    """

    def __init__(self, router_ns_id, interfaces, conf_dir):
        super().__init__(router_ns_id, interfaces, "zebra", conf_dir)

    def add_interface(self, interface):
        """
        Add interface command to config file
        """
        self.add_to_config(f"interface {interface}")

    def add_ip_address(self, ip_address):
        """
        Add IP address command to config file
        """
        if self.ipv6:
            self.add_to_config(f" ipv6 address {ip_address}")
        else:
            self.add_to_config(f" ip address {ip_address}")

    def create_basic_config(self):
        """
        Creates a file with basic configuration for OSPF.
        Use base `add_to_config` directly for more complex configurations
        """

        # Add loopback interface
        self.add_interface("lo")
        self.add_to_config(" no shutdown")
        for interface in self.interfaces:
            self.add_interface(interface.id)
            self.add_ip_address(interface.address.get_addr())
        self.create_config()

    def run(self):
        """
        Runs the zebra daemon
        """
        run_zebra(self.router_ns_id, self.conf_file, self.pid_file)
