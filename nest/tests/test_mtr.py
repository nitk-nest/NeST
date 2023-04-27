# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2023 NITK Surathkal

"""Test APIs from topology sub packages"""

import unittest
from nest.topology import Node, Router, connect
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper
from nest.routing.routing_helper import RoutingHelper
from nest.clean_up import delete_namespaces
from nest.topology_map import TopologyMap

# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=too-many-arguments


class TestTopologyMTR(unittest.TestCase):
    def setUp(self):
        self.h1 = Node("h1")
        self.h2 = Node("h2")
        self.r1 = Router("r1")
        self.r2 = Router("r2")

        AddressHelper.assign_addresses()
        RoutingHelper(protocol="static").populate_routing_tables()

    def tearDown(self):
        delete_namespaces()
        TopologyMap.delete_all_mapping()

    def test_p2p_MTR(self):
        n1 = Network("192.168.1.0/24")
        n2 = Network("192.168.2.0/24")
        n3 = Network("192.168.3.0/24")

        (_, _) = connect(self.h1, self.r1, network=n1)
        (_, _) = connect(self.r1, self.r2, network=n2)
        (_, eth2) = connect(self.r2, self.h2, network=n3)

        AddressHelper.assign_addresses()
        RoutingHelper(protocol="static").populate_routing_tables()

        status_list = []

        # Vary protocol option
        status_list.append(self.h1.mtr(eth2.address, protocol=""))
        status_list.append(self.h1.mtr(eth2.address, protocol="udp"))
        status_list.append(self.h1.mtr(eth2.address, protocol="tcp"))

        # Vary max_ttl
        status_list.append(self.h1.mtr(eth2.address, max_ttl=10))
        status_list.append(self.h1.mtr(eth2.address, max_ttl=20))
        status_list.append(self.h1.mtr(eth2.address, max_ttl=40))

        # Vary count
        status_list.append(self.h1.mtr(eth2.address, count=10))
        status_list.append(self.h1.mtr(eth2.address, count=20))
        status_list.append(self.h1.mtr(eth2.address, count=40))

        self.assertTrue(all(status_list))


if __name__ == "__main__":
    unittest.main()
