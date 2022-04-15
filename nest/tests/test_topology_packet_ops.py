# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal
"""Test APIs from topology packet operations"""

import unittest
from nest.topology import Node, connect
from nest.clean_up import delete_namespaces
from nest.topology_map import TopologyMap

# pylint: disable=invalid-name
# pylint: disable=missing-docstring


class TestTopologyPacketOps(unittest.TestCase):
    # Add rate in percent to get packet duplicated.
    def setUp(self):
        self.n0 = Node("n0")
        self.n1 = Node("n1")

    # Add rate in percent to get packet duplicated.
    def test_packet_duplication(self):
        (n0_n1, n1_n0) = connect(self.n0, self.n1)

        n0_n1.set_address("10.0.0.1/24")
        n1_n0.set_address("10.0.0.2/24")

        n0_n1.set_packet_duplication("20%")

        status = self.n0.ping("10.0.0.2")

        self.assertTrue(status)

    def test_packet_reordering(self):
        (n0_n1, n1_n0) = connect(self.n0, self.n1)

        n0_n1.set_address("10.0.0.1/24")
        n1_n0.set_address("10.0.0.2/24")

        n0_n1.set_attributes("10mbit", "10ms")

        n0_n1.set_packet_reorder("20%", gap=5)

        status = self.n0.ping("10.0.0.2", preload=10, packets=10)

        self.assertTrue(status)

    def tearDown(self):
        delete_namespaces()
        TopologyMap.delete_all_mapping()


if __name__ == "__main__":
    unittest.main()
