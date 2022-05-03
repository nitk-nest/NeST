# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""Test topology map API"""

import unittest
from nest.topology.device.device import Device
from nest.topology_map import TopologyMap
from nest.topology import Node, connect

# pylint: disable=missing-docstring
# pylint: disable=too-many-instance-attributes


class TestTopologyMap(unittest.TestCase):
    def setUp(self):
        # Create nodes
        ns1 = Node("n1")
        ns2 = Node("n2")

        # Get their corresponding ids and names
        self.ns_id1 = ns1.id
        self.ns_name1 = ns1.name
        self.ns_id2 = ns2.id
        self.ns_name2 = ns2.name

        # Create veth pairs (interfaces)
        (eth1, eth2) = connect(ns1, ns2)

        # Get their corresponding ids and names
        self.int_id1 = eth1.id
        self.int_name1 = eth1.name
        self.int_id2 = eth2.id
        self.int_name2 = eth2.name

    def tearDown(self):
        TopologyMap.delete_all_mapping()

    def test_add_and_get_node(self):
        self.assertEqual(TopologyMap.get_node(self.ns_id1).name, self.ns_name1)
        self.assertEqual(TopologyMap.get_node(self.ns_id2).name, self.ns_name2)

    def test_add_and_get_device(self):
        self.assertEqual(
            TopologyMap.get_device(self.ns_id1, self.int_id1).name, self.int_name1
        )
        self.assertEqual(
            TopologyMap.get_device(self.ns_id2, self.int_id2).name, self.int_name2
        )

    def test_add_same_entity_again(self):
        dummy_node = Node("nd")
        dummy_device = Device("device", None)

        with self.assertRaises(ValueError):
            TopologyMap.add_node(self.ns_id1, dummy_node)
        with self.assertRaises(ValueError):
            TopologyMap.add_device(self.ns_id1, self.int_id1, dummy_device)

    def test_delete_device(self):
        device = TopologyMap.get_device(self.ns_id1, self.int_id1)

        TopologyMap.delete_device(self.ns_id1, self.int_id1)
        with self.assertRaises(ValueError):
            TopologyMap.get_device(self.ns_id1, self.int_id1)

        TopologyMap.add_device(self.ns_id1, self.int_id1, device)
        self.assertEqual(
            TopologyMap.get_device(self.ns_id1, self.int_id1).name, self.int_name1
        )

    def test_move_device(self):
        TopologyMap.move_device(self.ns_id1, self.ns_id2, self.int_id1)

        with self.assertRaises(ValueError):
            TopologyMap.get_device(self.ns_id1, self.int_id1)

        self.assertEqual(
            TopologyMap.get_device(self.ns_id2, self.int_id1).name, self.int_name1
        )

        TopologyMap.move_device(self.ns_id2, self.ns_id1, self.int_id1)


if __name__ == "__main__":
    unittest.main()
