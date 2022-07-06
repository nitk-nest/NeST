# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""Test APIs from topology sub-package"""

import unittest
import subprocess

from nest.topology import Node, connect, Switch, Router
from nest.clean_up import delete_namespaces
from nest.topology_map import TopologyMap
from nest.routing.routing_helper import RoutingHelper
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper

# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=unused-variable
# pylint: disable=consider-using-with
# pylint: disable=too-many-instance-attributes


class TestIPv4AddressHelper(unittest.TestCase):
    def setUp(self):
        self.n0 = Node("n0")
        self.n1 = Node("n1")
        self.n2 = Node("n2")
        self.n3 = Node("n3")
        self.n4 = Node("n4")
        self.n5 = Node("n5")
        self.net1 = Network("10.0.1.0/24")
        self.net2 = Network("10.0.2.0/24")
        self.net3 = Network("2001:101::/122")
        self.net4 = Network("2002:101::/122")

    def tearDown(self):
        delete_namespaces()
        TopologyMap.delete_all_mapping()

    def test_p2p(self):
        (n0_n1, n1_n0) = connect(self.n0, self.n1, network=self.net1)

        AddressHelper.assign_addresses()

        status = self.n0.ping(n1_n0.get_address(), verbose=0)
        self.assertTrue(status)

    def test_p2p_ipv6(self):
        (n0_n1, n1_n0) = connect(self.n0, self.n1, network=self.net3)

        AddressHelper.assign_addresses()

        status = self.n0.ping(n1_n0.get_address(), verbose=0)
        self.assertTrue(status)

    def test_prp(self):
        # pylint: disable=invalid-name
        r = Node("r")
        r.enable_ip_forwarding()

        with self.net1:
            (n0_r, r_n0) = connect(self.n0, r)

        with self.net2:
            (r_n1, n1_r) = connect(r, self.n1, network=self.net2)

        AddressHelper.assign_addresses()

        self.n0.add_route("DEFAULT", n0_r)
        self.n1.add_route("DEFAULT", n1_r)

        status = self.n0.ping(n1_r.get_address(), verbose=0)

        self.assertTrue(status)

    def test_prp_ipv6(self):
        # pylint: disable=invalid-name
        r = Node("r")
        r.enable_ip_forwarding()

        with self.net3:
            (n0_r, r_n0) = connect(self.n0, r)

        with self.net4:
            (r_n1, n1_r) = connect(r, self.n1, network=self.net4)

        AddressHelper.assign_addresses()

        self.n0.add_route("DEFAULT", n0_r)
        self.n1.add_route("DEFAULT", n1_r)

        status = self.n0.ping(n1_r.get_address(), verbose=0)

        self.assertTrue(status)

    def test_prrp(self):
        # pylint: disable=invalid-name
        r1 = Node("r")
        r2 = Node("r")
        r1.enable_ip_forwarding()
        r2.enable_ip_forwarding()

        with self.net1:
            (n0_r1, r1_n0) = connect(self.n0, r1)

        (r1_r2, r2_r1) = connect(r1, r2, network=self.net2)
        (r2_n1, n1_r2) = connect(r2, self.n1)

        AddressHelper.assign_addresses()
        r2_n1.set_address("10.1.3.2/24")
        n1_r2.set_address("10.1.3.1/24")

        RoutingHelper(protocol="rip").populate_routing_tables()

        status = self.n0.ping(n1_r2.get_address(), verbose=0)

        self.assertTrue(status)

    def test_prrp_ipv6(self):
        # pylint: disable=invalid-name
        r1 = Node("r")
        r2 = Node("r")
        r1.enable_ip_forwarding()
        r2.enable_ip_forwarding()

        with self.net3:
            (n0_r1, r1_n0) = connect(self.n0, r1)

        (r1_r2, r2_r1) = connect(r1, r2, network=self.net4)
        (r2_n1, n1_r2) = connect(r2, self.n1)

        AddressHelper.assign_addresses()
        r2_n1.set_address("2003:101::10:1/122")
        n1_r2.set_address("2003:101::10:2/122")

        RoutingHelper(protocol="rip", ipv6_routing=True).populate_routing_tables()

        status = self.n0.ping(n1_r2.get_address(False, True, False), verbose=0)

        self.assertTrue(status)

    def test_tcp_param(self):
        self.n0.configure_tcp_param("ecn", "1")
        ecn = self.n0.read_tcp_param("ecn")
        self.assertEqual(ecn, "1")

    def test_run_inside_node(self):
        (n0_n1, n1_n0) = connect(self.n0, self.n1, network=self.net1)

        AddressHelper.assign_addresses()

        # Run ping from self.n0 to self.n1
        with self.n0:
            command = f"ping -c 1 {n1_n0.address.get_addr(with_subnet=False)}"
            proc = subprocess.Popen(
                command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            (stdout, _) = proc.communicate()

        self.assertEqual(stdout[:4], b"PING", "Invalid ping output")

    def test_ip_addr_to_switch(self):
        # pylint: disable=too-many-locals
        s1 = Switch("s1")
        s2 = Switch("s2")
        r1 = Router("r1")

        with self.net1:
            (n0_s1, s1_n0) = connect(self.n0, s1)
            (n1_s1, s1_n1) = connect(self.n1, s1)
            (n2_s1, s1_n2) = connect(self.n2, s1)
            (s1_r1, r1_s1) = connect(s1, r1)

        with self.net2:
            (n3_s2, s2_n3) = connect(self.n3, s2)
            (n4_s2, s2_n4) = connect(self.n4, s2)
            (n5_s2, s2_n5) = connect(self.n5, s2)
            (s2_r1, r1_s2) = connect(s2, r1)

        AddressHelper.assign_addresses()

        self.n0.add_route("DEFAULT", n0_s1, r1_s1.address)
        self.n1.add_route("DEFAULT", n1_s1, r1_s1.address)
        self.n2.add_route("DEFAULT", n2_s1, r1_s1.address)
        self.n3.add_route("DEFAULT", n3_s2, r1_s2.address)
        self.n4.add_route("DEFAULT", n4_s2, r1_s2.address)
        self.n5.add_route("DEFAULT", n5_s2, r1_s2.address)

        # `Ping` from `n0` to 'n3', `n1` to `n4`, and `n2` to `n5`
        status_1 = self.n0.ping(n3_s2.address)
        status_2 = self.n1.ping(n4_s2.address)
        status_3 = self.n2.ping(n5_s2.address)

        self.assertTrue(status_1)
        self.assertTrue(status_2)
        self.assertTrue(status_3)


if __name__ == "__main__":
    unittest.main()
