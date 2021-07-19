# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Test APIs from mpls static routing"""

import subprocess
import unittest
from nest.topology import Node, connect
from nest.clean_up import delete_namespaces

# pylint: disable=missing-docstring


class TestStaticMPLS(unittest.TestCase):
    # pylint: disable=invalid-name
    def setUp(self):

        self.assertTrue(
            "mpls_iptunnel" in subprocess.check_output("lsmod").decode(),
            "Couldn't load mpls",
        )

        self.n0 = Node("n0")
        self.n1 = Node("n1")
        self.r0 = Node("r0")
        self.r1 = Node("r1")
        self.r0.enable_ip_forwarding()
        self.r1.enable_ip_forwarding()

    def tearDown(self):
        delete_namespaces()

        ### Create interfaces and connect nodes and routers ###

    def test_routing(self):
        (eth_n0_r0, eth_r0_n0) = connect(self.n0, self.r0, "eth-n0_r0", "eth-r0_n0")
        (eth_r0_r1, eth_r1_r0) = connect(self.r0, self.r1, "eth-r0r1-0", "eth-r1r0-0")
        (eth_r1_n1, eth_n1_r1) = connect(self.r1, self.n1, "eth-r1n1-0", "eth-n1r1-0")

        ### Assign addresses to interfaces ###
        eth_n0_r0.set_address("10.0.1.1/24")
        eth_r0_n0.set_address("10.0.1.2/24")

        eth_r0_r1.set_address("10.0.2.2/24")
        eth_r1_r0.set_address("10.0.2.3/24")

        eth_r1_n1.set_address("10.0.3.3/24")
        eth_n1_r1.set_address("10.0.3.4/24")

        # Enable MPLS on all interfaces
        eth_n0_r0.enable_mpls()
        eth_r0_n0.enable_mpls()

        eth_r0_r1.enable_mpls()
        eth_r1_r0.enable_mpls()

        eth_r1_n1.enable_mpls()
        eth_n1_r1.enable_mpls()

        # Add routes(mpls family)
        self.n0.add_route_mpls_push("10.0.3.0/24", eth_r0_n0.get_address(), 101)
        self.r0.add_route_mpls_switch(101, eth_r1_r0.get_address(), 102)
        self.r1.add_route_mpls_pop(102, eth_n1_r1.get_address())

        self.n1.add_route_mpls_push("10.0.1.0/24", eth_r1_n1.get_address(), 201)
        self.r1.add_route_mpls_switch(201, eth_r0_r1.get_address(), 202)
        self.r0.add_route_mpls_pop(202, eth_n0_r0.get_address())

        status = self.n0.ping("10.0.3.4", verbose=True)
        self.assertTrue(status)

        status = self.n1.ping("10.0.1.1", verbose=True)
        self.assertTrue(status)


if __name__ == "__main__":
    unittest.main()
