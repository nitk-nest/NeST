# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Test APIs from routing sub-package"""
import unittest
from glob import glob
from os.path import isfile
from nest import config
from nest.topology_map import TopologyMap
from nest.topology import Node, connect
from nest.routing.routing_helper import RoutingHelper
from nest.clean_up import delete_namespaces

# pylint: disable=missing-docstring
class TestFrr(unittest.TestCase):

    # pylint: disable=invalid-name
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

        eth_p1r1.set_address("10.0.1.1/24")
        eth_r1p1.set_address("10.0.1.2/24")

        eth_r1r2.set_address("10.0.2.2/24")
        eth_r2r1.set_address("10.0.2.3/24")

        eth_r2p2.set_address("10.0.3.3/24")
        eth_p2r2.set_address("10.0.3.4/24")

        config.set_value("routing_suite", "frr")  # Use frr

        self.routing_helper = None

    def tearDown(self):
        delete_namespaces()
        TopologyMap.delete_all_mapping()
        if self.routing_helper:
            # pylint: disable=protected-access
            self.routing_helper._clean_up()

    def test_routing_helper(self):

        self.routing_helper = RoutingHelper("rip")
        self.routing_helper.populate_routing_tables()

        status = self.n0.ping("10.0.3.4", verbose=0)
        self.assertTrue(status)

        status = self.n1.ping("10.0.1.1", verbose=0)
        self.assertTrue(status)

    def test_ospf(self):
        self.routing_helper = RoutingHelper("ospf")
        self.routing_helper.populate_routing_tables()

        status = self.n0.ping("10.0.3.4", verbose=0)
        self.assertTrue(status)

        status = self.n1.ping("10.0.1.1", verbose=0)
        self.assertTrue(status)

    def test_isis(self):
        self.routing_helper = RoutingHelper("isis")
        self.routing_helper.populate_routing_tables()

        status = self.n0.ping("10.0.3.4", verbose=0)
        self.assertTrue(status)

        status = self.n1.ping("10.0.1.1", verbose=0)
        self.assertTrue(status)

    def test_babel(self):
        with self.assertRaises(ValueError) as ex:
            RoutingHelper("babel").populate_routing_tables()

        self.assertEqual(
            str(ex.exception),
            "Supported routing protocols are rip, ospf, isis and static, "
            "but got protocol babel",
        )

    def test_static(self):
        RoutingHelper("static").populate_routing_tables()

        status = self.n0.ping("10.0.3.4", verbose=0)
        self.assertTrue(status)

        status = self.n1.ping("10.0.1.1", verbose=0)
        self.assertTrue(status)

    def test_logs(self):
        config.set_value("routing_logs", True)

        self.routing_helper = RoutingHelper("rip")
        self.routing_helper.populate_routing_tables()

        self.assertTrue(len(glob(f"{config.get_value('routing_suite')}-logs_*")) > 0)

        config.set_value("routing_logs", False)


if __name__ == "__main__":
    unittest.main()
