# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Class to handles OSPF related functionalities"""

from nest.engine.quagga import run_ospfd
from nest.routing.quagga_base import QuaggaBase


class Ospf(QuaggaBase):
    """
    Handles OSPF related functionalities for Quagga.
    """

    def __init__(self, router_ns_id, interfaces, conf_dir):
        super().__init__(router_ns_id, interfaces, 'ospfd', conf_dir)

    def create_basic_config(self):
        """
        Creates a file with basic configuration for OSPF.
        Use base `add_to_config` directly for more complex configurations
        """
        for interface in self.interfaces:
            self.add_to_config(f'interface {interface.id}')

        self.add_to_config('router ospf')
        self.add_to_config(
            f'ospf router-id {self.interfaces[0].address.get_addr(with_subnet=False)}')
        for interface in self.interfaces:
            self.add_to_config(
                f' network {interface.address.get_subnet()} area 0.0.0.0')

        self.create_config()

    def run(self):
        """
        Runs the ospfd command
        """
        run_ospfd(self.router_ns_id, self.conf_file, self.pid_file)
