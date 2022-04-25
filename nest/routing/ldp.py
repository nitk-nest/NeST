# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""Class to handles Ldp related functionalities"""

from functools import partial
from nest.engine.dynamic_routing import run_ldpd
from nest.routing.route_daemons import RoutingDaemonBase


class Ldp(RoutingDaemonBase):
    """
    Handles Ldp related functionalities for frr.
    """

    def __init__(self, router_ns_id, ipv6_routing, interfaces, conf_dir, **kwargs):
        super().__init__(
            router_ns_id, ipv6_routing, interfaces, "ldpd", conf_dir, **kwargs
        )

    def create_basic_config(self):
        """
        Creates a file with basic configuration for ldp.
        Use base `add_to_config` directly for more complex configurations
        """
        self.add_to_config("mpls ldp")
        router_ip = self.interfaces[0].get_address(
            not self.ipv6_routing, self.ipv6_routing, True
        )[0]
        self.add_to_config(f" router-id {router_ip.get_addr(with_subnet=False)}")
        if not self.ipv6_routing:
            self.add_to_config(" address-family ipv4")
        else:
            self.add_to_config(" address-family ipv6")
        self.add_to_config(
            f"discovery transport-address {router_ip.get_addr(with_subnet=False)}"
        )

        for interface in self.interfaces:
            if self.ipv6_routing and len(interface.get_address(False, True, True)) > 0:
                self.add_to_config(f"  interface {interface.id}")
            elif (
                not self.ipv6_routing
                and len(interface.get_address(True, False, True)) > 0
            ):
                self.add_to_config(f"  interface {interface.id}")

        if self.log_file is not None:
            self.add_to_config(f"log file {self.log_file}")

        self.create_config()

    def run(self):
        """
        Runs the ldpd command
        """
        super().run(
            engine_func=partial(
                run_ldpd, self.router_ns_id, self.conf_file, self.pid_file
            )
        )
