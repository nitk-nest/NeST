# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Test APIs from static routing"""

import unittest
from nest.topology import Node, connect
from nest.clean_up import delete_namespaces
from nest.topology_map import TopologyMap
from nest.routing.routing_helper import RoutingHelper

# pylint: disable=missing-docstring


class TestStaticRouting(unittest.TestCase):
    # pylint: disable=invalid-name
    def setUp(self):
        # create nodes
        # pylint: disable=anomalous-backslash-in-string
        """
        Topology is as follows:

        n0            n2
          \          /
           \        /
            r0----r1
           /        \
          /          \
        n1            n3
        """

        self.n0 = Node("n0")
        self.n1 = Node("n1")
        self.n2 = Node("n2")
        self.n3 = Node("n3")

        self.r0 = Node("r0")
        self.r1 = Node("r1")
        self.r0.enable_ip_forwarding()
        self.r1.enable_ip_forwarding()

        # populated later when we set the addresses
        # to be used for pairwise ping tests
        self.nodes_addresses = []

        (eth_n0_r0, eth_r0_n0) = connect(self.n0, self.r0, "eth-n0_r0", "eth-r0_n0")
        (eth_n1_r0, eth_r0_n1) = connect(self.n1, self.r0, "eth-n1_r0", "eth-r0_n1")

        (eth_r0_r1, eth_r1_r0) = connect(self.r0, self.r1, "eth-r0_r1", "eth-r1_r0")

        (eth_n2_r1, eth_r1_n2) = connect(self.n2, self.r1, "eth-n2_r1", "eth-r1_n2")
        (eth_n3_r1, eth_r1_n3) = connect(self.n3, self.r1, "eth-n3_r1", "eth-r1_n3")

        ### Assign addresses to interfaces ###
        eth_n0_r0.set_address("10.0.1.1/24")
        eth_r0_n0.set_address("10.0.1.2/24")
        self.nodes_addresses.append((self.n0, "10.0.1.1"))

        eth_n1_r0.set_address("10.0.1.3/24")
        eth_r0_n1.set_address("10.0.1.4/24")
        self.nodes_addresses.append((self.n1, "10.0.1.3"))

        eth_r0_r1.set_address("10.0.2.5/24")
        eth_r1_r0.set_address("10.0.2.6/24")

        eth_r1_n2.set_address("10.0.3.7/24")
        eth_n2_r1.set_address("10.0.3.8/24")
        self.nodes_addresses.append((self.n2, "10.0.3.8"))

        eth_r1_n3.set_address("10.0.3.9/24")
        eth_n3_r1.set_address("10.0.3.10/24")
        self.nodes_addresses.append((self.n3, "10.0.3.10"))

    def tearDown(self):
        delete_namespaces()
        TopologyMap.delete_all_mapping()

        ### Create interfaces and connect nodes and routers ###

    def test_routing(self):
        # this runs a DFS algorithm and populates routing tables accordingly
        # If the graph is a tree, there is only one path for each pair\
        # for non-trees, this will use a spanning tree found by DFS
        RoutingHelper("static").populate_routing_tables()

        # Ping between each pair of nodes
        for node1, address1 in self.nodes_addresses:
            for _, address2 in self.nodes_addresses:
                if address1 != address2:
                    status = node1.ping(address2, verbose=2)
                    self.assertTrue(status)


if __name__ == "__main__":
    unittest.main()
