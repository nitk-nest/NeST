# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Class to handles IS-IS related functionalities"""

import hashlib
from functools import partial
from nest.engine.dynamic_routing import run_isisd
from nest.routing.route_daemons import RoutingDaemonBase


class Isis(RoutingDaemonBase):
    """
    Handles IS-IS related functionalities.
    """

    def __init__(self, router_ns_id, ipv6_routing, interfaces, conf_dir, **kwargs):
        super().__init__(
            router_ns_id, ipv6_routing, interfaces, "isisd", conf_dir, **kwargs
        )

    def create_basic_config(self):
        """
        Creates a file with basic configuration for IS-IS.
        Use base `add_to_config` directly for more complex configurations
        """

        area_id = "00.0000.0000.0000.0000.0000.0000"
        system_id_hash = str(
            int(
                hashlib.sha256(
                    self.interfaces[0]
                    .get_address(not self.ipv6_routing, self.ipv6_routing, True)[0]
                    .get_addr(with_subnet=False)
                    .encode("utf-8")
                ).hexdigest(),
                16,
            )
        )[:12]

        system_id = ".".join(map("".join, zip(*[iter(system_id_hash)] * 4)))
        self.add_to_config(f"router isis {self.router_ns_id}")
        self.add_to_config("is-type level-1")
        self.add_to_config(f"net {area_id}.{system_id}.00")
        for interface in self.interfaces:
            self.add_to_config(f"interface {interface.id}")
            if self.ipv6_routing:
                self.add_to_config(f" ipv6 router isis {self.router_ns_id}")
            else:
                self.add_to_config(f" ip router isis {self.router_ns_id}")

        if self.log_file is not None:
            self.add_to_config(f"log file {self.log_file}")

    def run(self):
        """
        Runs the isisd command
        """
        super().run(
            engine_func=partial(
                run_isisd, self.router_ns_id, self.conf_file, self.pid_file
            )
        )
