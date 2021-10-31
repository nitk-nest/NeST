# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Class to handles OSPF related functionalities"""

import random
from functools import partial
from nest.engine.dynamic_routing import run_ospfd
from nest.routing.route_daemons import RoutingDaemonBase
from nest import config

# pylint: disable=line-too-long


class Ospf(RoutingDaemonBase):
    """
    Handles OSPF related functionalities.
    """

    def __init__(self, router_ns_id, ipv6_routing, interfaces, conf_dir, **kwargs):
        if config.get_value("routing_suite") == "bird":
            super().__init__(
                router_ns_id, ipv6_routing, interfaces, "bird", conf_dir, **kwargs
            )
        else:
            super().__init__(
                router_ns_id, ipv6_routing, interfaces, "ospfd", conf_dir, **kwargs
            )

    # pylint: disable=too-many-branches
    def create_basic_config(self):
        """
        Creates a file with basic configuration for OSPF.
        Use base `add_to_config` directly for more complex configurations
        """
        if config.get_value("routing_suite") == "bird":
            if not self.ipv6_routing:
                self.conf.write(
                    "protocol kernel{\n\tipv4{\n\t\texport all;\n\t};\n\tpersist;\n\tlearn;\n}\n"
                )
                self.conf.write("protocol static{\n\tipv4;\n}\n")
                self.conf.write("protocol device{\n}\n")
                self.conf.write(
                    'protocol ospf v2{\n\tarea 0{\n\t\tinterface "*"{\n\t\t\ttype pointopoint;\n\t\t};\n\t};\n}\n'
                )
            else:
                self.conf.write(
                    "protocol kernel{\n\tipv6{\n\t\texport all;\n\t};\n\tpersist;\n\tlearn;\n}\n"
                )
                self.conf.write("protocol static{\n\tipv6;\n}\n")
                self.conf.write("protocol device{\n}\n")
                self.conf.write(
                    'protocol ospf v3{\n\tarea 0{\n\t\tinterface "*"{\n\t\t\ttype pointopoint;\n\t\t};\n\t};\n}\n'
                )
        else:
            if self.ipv6_routing:
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
                    f"ospf router-id {self.interfaces[0].get_address(not self.ipv6_routing, self.ipv6_routing, True)[0].get_addr(with_subnet=False)}"
                )
                for interface in self.interfaces:
                    self.add_to_config(
                        f" network {interface.get_address(not self.ipv6_routing, self.ipv6_routing, True)[0].get_subnet()} area 0.0.0.0"
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
                run_ospfd,
                self.router_ns_id,
                self.conf_file,
                self.pid_file,
                self.ipv6_routing,
                log_file=self.log_file,
                socket_file=self.socket_file,
            )
        )
