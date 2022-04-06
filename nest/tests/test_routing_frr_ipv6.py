# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Test APIs from routing sub-package"""
import unittest
from os.path import isfile
from nest import config
from nest.topology_map import TopologyMap
from nest.topology import Node, connect
from nest.routing.routing_helper import RoutingHelper
from nest.clean_up import delete_namespaces

# pylint: disable=missing-docstring
class TestFrr(unittest.TestCase):

    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    def setUp(self):

        self.assertTrue(isfile("/usr/lib/frr/zebra"), "Frrouting is not installed")

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

        eth_p1r1.set_address("10::1:1/122")
        eth_r1p1.set_address("10::1:2/122")

        eth_r1r2.set_address("10::2:2/122")
        eth_r2r1.set_address("10::2:3/122")

        eth_r2p2.set_address("10::3:3/122")
        eth_p2r2.set_address("10::3:4/122")

        config.set_value("routing_suite", "frr")  # Use frr
        self.routing_helper = None

    def tearDown(self):
        delete_namespaces()
        TopologyMap.delete_all_mapping()
        if self.routing_helper:
            # pylint: disable=protected-access
            self.routing_helper._clean_up()

    def test_rip_ipv6(self):

        self.routing_helper = RoutingHelper("rip", ipv6_routing=True)
        self.routing_helper.populate_routing_tables()

        status = self.n0.ping("10::3:4", verbose=0)
        self.assertTrue(status)

        status = self.n1.ping("10::1:1", verbose=0)
        self.assertTrue(status)

    def test_ospf_ipv6(self):

        self.routing_helper = RoutingHelper("ospf", ipv6_routing=True)
        self.routing_helper.populate_routing_tables()

        status = self.n0.ping("10::3:4", verbose=0)
        self.assertTrue(status)

        status = self.n1.ping("10::1:1", verbose=0)
        self.assertTrue(status)

    def test_isis_ipv6(self):
        self.routing_helper = RoutingHelper("isis", ipv6_routing=True)
        self.routing_helper.populate_routing_tables()

        status = self.n0.ping("10::3:4", verbose=0)
        self.assertTrue(status)

        status = self.n1.ping("10::1:1", verbose=0)
        self.assertTrue(status)


if __name__ == "__main__":
    unittest.main()
