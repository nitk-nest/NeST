# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Test APIs from routing sub-package"""

import unittest
from nest import config
from nest.topology_map import TopologyMap
from nest.topology import Node, connect
from nest.routing.routing_helper import RoutingHelper
from nest.clean_up import delete_namespaces

# pylint: disable=missing-docstring


class TestQuagga(unittest.TestCase):

    # pylint: disable=invalid-name
    def setUp(self):
        self.n0 = Node("n0")
        self.n1 = Node("n1")
        self.r0 = Node("r0")
        self.r1 = Node("r1")
        self.r0.enable_ip_forwarding()
        self.r1.enable_ip_forwarding()

        ### Create interfaces and connect nodes and routers ###

        (eth_p1r1, eth_r1p1) = connect(self.n0, self.r0, "eth-n1r1-0", "eth-r1n1-0")
        (eth_r1r2, eth_r2r1) = connect(self.r0, self.r1, "eth-r1r2-0", "eth-r2r1-0")
        (eth_r2p2, eth_p2r2) = connect(self.r1, self.n1, "eth-r2n2-0", "eth-n2r2-0")

        ### Assign addresses to interfaces ###

        eth_p1r1.set_address(["10.0.1.1/24", "10::1:1/122"])
        eth_r1p1.set_address(["10.0.1.2/24", "10::1:2/122"])

        eth_r1r2.set_address(["10.0.2.2/24", "10::2:2/122"])
        eth_r2r1.set_address(["10.0.2.3/24", "10::2:3/122"])

        eth_r2p2.set_address(["10.0.3.3/24", "10::3:3/122"])
        eth_p2r2.set_address(["10.0.3.4/24", "10::3:4/122"])

        config.set_value("routing_suite", "quagga")  # Use quagga

        self.routing_helper_ipv4 = None
        self.routing_helper_ipv6 = None

    def tearDown(self):
        delete_namespaces()
        TopologyMap.delete_all_mapping()
        if self.routing_helper_ipv4:
            # pylint: disable=protected-access
            self.routing_helper_ipv4._clean_up()
        if self.routing_helper_ipv6:
            # pylint: disable=protected-access
            self.routing_helper_ipv6._clean_up()

    def test_routing_helper(self):

        self.routing_helper_ipv4 = RoutingHelper("rip")
        self.routing_helper_ipv6 = RoutingHelper("rip", ipv6_routing=True)
        self.routing_helper_ipv4.populate_routing_tables()
        self.routing_helper_ipv6.populate_routing_tables()

        status_ipv4 = self.n0.ping("10.0.3.4", verbose=False)
        self.assertTrue(status_ipv4)
        status_ipv6 = self.n0.ping("10::3:4", verbose=False)
        self.assertTrue(status_ipv6)

        status_ipv4 = self.n0.ping("10.0.1.1", verbose=False)
        self.assertTrue(status_ipv4)
        status_ipv6 = self.n1.ping("10::1:1", verbose=False)
        self.assertTrue(status_ipv6)

    def test_ospf(self):
        self.routing_helper_ipv4 = RoutingHelper("ospf")
        self.routing_helper_ipv6 = RoutingHelper("ospf", ipv6_routing=True)
        self.routing_helper_ipv4.populate_routing_tables()
        self.routing_helper_ipv6.populate_routing_tables()

        status_ipv4 = self.n0.ping("10.0.3.4", verbose=False)
        self.assertTrue(status_ipv4)
        status_ipv6 = self.n0.ping("10::3:4", verbose=False)
        self.assertTrue(status_ipv6)

        status_ipv4 = self.n0.ping("10.0.1.1", verbose=False)
        self.assertTrue(status_ipv4)
        status_ipv6 = self.n1.ping("10::1:1", verbose=False)
        self.assertTrue(status_ipv6)

    def test_isis(self):
        self.routing_helper_ipv4 = RoutingHelper("isis")
        self.routing_helper_ipv6 = RoutingHelper("isis", ipv6_routing=True)
        self.routing_helper_ipv4.populate_routing_tables()

        status_ipv4 = self.n0.ping("10.0.3.4", verbose=False)
        self.assertTrue(status_ipv4)
        status_ipv4 = self.n0.ping("10.0.1.1", verbose=False)
        self.assertTrue(status_ipv4)

        self.routing_helper_ipv6.populate_routing_tables()

        status_ipv6 = self.n0.ping("10::3:4", verbose=False)
        self.assertTrue(status_ipv6)
        status_ipv6 = self.n1.ping("10::1:1", verbose=False)
        self.assertTrue(status_ipv6)


if __name__ == "__main__":
    unittest.main()
