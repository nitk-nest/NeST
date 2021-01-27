# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Test topology map API"""

import unittest
from nest.topology_map import TopologyMap

# pylint: disable=missing-docstring
# pylint: disable=too-many-instance-attributes


class TestTopologyMap(unittest.TestCase):
    def setUp(self):
        # Define namespace id and names
        self.ns_id1 = "ns_id1"
        self.ns_id2 = "ns_id2"
        self.ns_name1 = "ns_name1"
        self.ns_name2 = "ns_name2"

        # Add namespaces
        TopologyMap.add_namespace(self.ns_id1, self.ns_name1)
        TopologyMap.add_namespace(self.ns_id2, self.ns_name2)

        # Define interface id and names
        self.int_id1 = "int_id1"
        self.int_id2 = "int_id2"
        self.int_name1 = "int_name1"
        self.int_name2 = "int_name2"

        # Add interfaces
        TopologyMap.add_interface(self.ns_id1, self.int_id1, self.int_name1)
        TopologyMap.add_interface(self.ns_id1, self.int_id2, self.int_name2)

    def tearDown(self):
        TopologyMap.delete_all_mapping()

    def test_add_and_get_namespace(self):
        self.assertEqual(TopologyMap.get_namespace(self.ns_id1)["name"], self.ns_name1)
        self.assertEqual(TopologyMap.get_namespace(self.ns_id2)["name"], self.ns_name2)

    def test_add_and_get_interface(self):
        self.assertEqual(
            TopologyMap.get_interface(self.ns_id1, self.int_id1)["name"], self.int_name1
        )
        self.assertEqual(
            TopologyMap.get_interface(self.ns_id1, self.int_id2)["name"], self.int_name2
        )

    def test_add_same_entity_again(self):
        with self.assertRaises(ValueError):
            TopologyMap.add_namespace(self.ns_id1, self.ns_name1)
        with self.assertRaises(ValueError):
            TopologyMap.add_interface(self.ns_id1, self.int_id1, self.int_name1)


if __name__ == "__main__":
    unittest.main()
