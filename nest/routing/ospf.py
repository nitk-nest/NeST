# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Class to handles OSPF related functionalities"""

import random
from functools import partial
from nest.engine.dynamic_routing import run_ospfd
from nest.routing.route_daemons import RoutingDaemonBase
import nest.config as config


class Ospf(RoutingDaemonBase):
    """
    Handles OSPF related functionalities.
    """

    def __init__(self, router_ns_id, interfaces, conf_dir, **kwargs):
        super().__init__(router_ns_id, interfaces, "ospfd", conf_dir, **kwargs)

    def create_basic_config(self):
        """
        Creates a file with basic configuration for OSPF.
        Use base `add_to_config` directly for more complex configurations
        """
        if self.ipv6:
            for interface in self.interfaces:
                self.add_to_config(f"interface {interface.id}")
                # send hello packets every 1 second for faster convergence
                self.add_to_config("ipv6 ospf6 hello-interval 1")

            self.add_to_config("router ospf6")

            # Generates random router-id in A.B.C.D format
            router_id = ".".join(
                map(str, (random.randint(0, 255) for _ in range(0, 4)))
            )
            # for quagga
            if config.get_value("routing_suite") == "quagga":
                self.add_to_config(f"router-id {router_id}")
            # for frr
            else:
                self.add_to_config(f"ospf6 router-id {router_id}")
            for interface in self.interfaces:
                self.add_to_config(f" interface {interface.id} area 0.0.0.0")
        else:
            for interface in self.interfaces:
                self.add_to_config(f"interface {interface.id}")
                # send hello packets every 1 second for faster convergence
                self.add_to_config("ip ospf hello-interval 1")

            self.add_to_config("router ospf")
            self.add_to_config(
                f"ospf router-id {self.interfaces[0].address.get_addr(with_subnet=False)}"
            )
            for interface in self.interfaces:
                self.add_to_config(
                    f" network {interface.address.get_subnet()} area 0.0.0.0"
                )

        if self.log_file is not None:
            self.add_to_config(f"log file {self.log_file}")

        self.create_config()

    def run(self):
        """
        Runs the ospfd command
        """
        super().run(
            engine_func=partial(
                run_ospfd, self.router_ns_id, self.conf_file, self.pid_file, self.ipv6
            )
        )
