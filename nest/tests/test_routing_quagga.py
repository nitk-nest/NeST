# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Test APIs from routing sub-package"""

import unittest
from glob import glob
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

        eth_p1r1.set_address("10.0.1.1/24")
        eth_r1p1.set_address("10.0.1.2/24")

        eth_r1r2.set_address("10.0.2.2/24")
        eth_r2r1.set_address("10.0.2.3/24")

        eth_r2p2.set_address("10.0.3.3/24")
        eth_p2r2.set_address("10.0.3.4/24")

        config.set_value("routing_suite", "quagga")  # Use quagga

    def tearDown(self):
        delete_namespaces()
        TopologyMap.delete_all_mapping()

    def test_routing_helper(self):

        RoutingHelper("rip").populate_routing_tables()

        status = self.n0.ping("10.0.3.4", verbose=False)
        self.assertTrue(status)

        status = self.n1.ping("10.0.1.1", verbose=False)
        self.assertTrue(status)

    def test_ospf(self):
        RoutingHelper("ospf").populate_routing_tables()

        status = self.n0.ping("10.0.3.4", verbose=False)
        self.assertTrue(status)

        status = self.n1.ping("10.0.1.1", verbose=False)
        self.assertTrue(status)

    def test_isis(self):
        RoutingHelper("isis").populate_routing_tables()

        status = self.n0.ping("10.0.3.4", verbose=False)
        self.assertTrue(status)

        status = self.n1.ping("10.0.1.1", verbose=False)
        self.assertTrue(status)

    def test_logs(self):
        config.set_value("routing_logs", True)

        RoutingHelper("rip").populate_routing_tables()

        self.assertTrue(len(glob(f"{config.get_value('routing_suite')}-logs_*")) > 0)

        config.set_value("routing_logs", False)

    def test_custom_node_routers(self):
        RoutingHelper(
            "rip", [self.n0, self.n1], [self.r0, self.r1]
        ).populate_routing_tables()

        status = self.n0.ping("10.0.3.4", verbose=False)
        self.assertTrue(status)

        status = self.n1.ping("10.0.1.1", verbose=False)
        self.assertTrue(status)

        with self.assertRaises(TypeError):
            RoutingHelper("rip", self.n1, self.r1).populate_routing_tables()

        with self.assertRaises(ValueError):
            RoutingHelper("rip", ["n1"], ["r1"]).populate_routing_tables()


if __name__ == "__main__":
    unittest.main()
