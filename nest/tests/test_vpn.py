# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2023 NITK Surathkal

"""
Test APIs for VPN.
"""

import unittest
import warnings
from nest.topology import Node, connect, Router
from nest.clean_up import delete_namespaces
from nest.topology_map import TopologyMap
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper
from nest.topology.vpn import connect_vpn

# pylint: disable=invalid-name
# pylint: disable=unused-variable
# pylint: disable=unbalanced-tuple-unpacking
# pylint: disable=too-many-instance-attributes


class TestVPN(unittest.TestCase):
    """
    Test case for VPN API.
    """

    def setUp(self):
        """
        Set up the test case.
        """
        warnings.filterwarnings("ignore", category=ResourceWarning)

        self.h1 = Node("h1")
        self.h2 = Node("h2")
        self.r1 = Router("r1")
        self.r2 = Router("r2")
        self.net1 = Network("192.168.1.0/24")
        self.net2 = Network("192.168.2.0/24")
        self.net3 = Network("192.168.3.0/24")
        self.vpn_network = Network("10.200.0.0/24")

        (eth1, etr1a) = connect(self.h1, self.r1, network=self.net1)
        (etr1b, etr2a) = connect(self.r1, self.r2, network=self.net2)
        (etr2b, eth2) = connect(self.r2, self.h2, network=self.net3)

        AddressHelper.assign_addresses()

        self.h1.add_route("DEFAULT", eth1)
        self.h2.add_route("DEFAULT", eth2)
        self.r1.add_route("DEFAULT", etr1b)
        self.r2.add_route("DEFAULT", etr2a)

    def tearDown(self):
        """
        Tear down the test case.
        """
        delete_namespaces()
        TopologyMap.delete_all_mapping()

    def test_vpn(self):
        """
        Test the VPN API.
        """
        (h1tun, h2tun) = connect_vpn(self.h1, self.h2, network=self.vpn_network)
        status = self.h2.ping(h1tun.get_address(), verbose=0)
        self.assertTrue(status)


if __name__ == "__main__":
    unittest.main()
