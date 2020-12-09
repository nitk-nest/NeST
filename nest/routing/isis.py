# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Class to handles IS-IS related functionalities"""

import hashlib
from nest.engine.quagga import run_isisd
from nest.routing.quagga_base import QuaggaBase


class Isis(QuaggaBase):
    """
    Handles IS-IS related functionalities for Quagga.
    """

    def __init__(self, router_ns_id, interfaces, conf_dir):
        super().__init__(router_ns_id, interfaces, 'isisd', conf_dir)

    def create_basic_config(self):
        """
        Creates a file with basic configuration for IS-IS.
        Use base `add_to_config` directly for more complex configurations
        """

        area_id = '00.0000.0000.0000.0000.0000.0000'
        system_id_hash = str(int(hashlib.sha256(self.interfaces[0].address.get_addr(
            with_subnet=False).encode('utf-8')).hexdigest(), 16))[:12]
        system_id = '.'.join(map(''.join, zip(*[iter(system_id_hash)]*4)))

        self.add_to_config('router isis {self.router_ns_id}')
        self.add_to_config('is-type level-1')
        self.add_to_config(
            f'net {area_id}.{system_id}.00')
        for interface in self.interfaces:
            self.add_to_config(f'interface {interface.id}')
            self.add_to_config(' ip router isis {self.router_ns_id}')

        self.create_config()

    def run(self):
        """
        Runs the isisd command
        """
        run_isisd(self.router_ns_id, self.conf_file, self.pid_file)
