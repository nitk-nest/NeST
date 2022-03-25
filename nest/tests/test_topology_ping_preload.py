# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""Test APIs from topology sub packages"""

import unittest
from nest.topology import Node, connect
from nest.clean_up import delete_namespaces
from nest.topology_map import TopologyMap

# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=too-many-arguments


class TestTopologyPingPreload(unittest.TestCase):
    def setUp(self):
        self.n0 = Node("n0")
        self.n1 = Node("n1")

    def tearDown(self):
        delete_namespaces()
        TopologyMap.delete_all_mapping()

    def test_p2p_ping_preload(self):
        (n0_n1, n1_n0) = connect(self.n0, self.n1)

        n0_n1.set_address("10.0.0.1/24")
        n1_n0.set_address("10.0.0.2/24")

        status = self.n0.ping("10.0.0.2", preload=10, packets=10)

        self.assertTrue(status)


if __name__ == "__main__":
    unittest.main()
