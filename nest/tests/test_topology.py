# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Test APIs from topology sub-package"""

import unittest
from nest.topology import Node, connect
from nest.clean_up import delete_namespaces
from nest.topology_map import TopologyMap

#pylint: disable=missing-docstring
#pylint: disable=invalid-name
class TestTopology(unittest.TestCase):

    def setUp(self):
        self.n0 = Node('n0')
        self.n1 = Node('n1')

    def tearDown(self):
        delete_namespaces()
        TopologyMap.delete_all_mapping()


    def test_p2p(self):
        (n0_n1, n1_n0) = connect(self.n0, self.n1)

        n0_n1.set_address('10.0.0.1/24')
        n1_n0.set_address('10.0.0.2/24')

        status = self.n0.ping('10.0.0.2', verbose=False)

        self.assertTrue(status)

    def test_prp(self):
        # pylint: disable=invalid-name
        r = Node('r')
        r.enable_ip_forwarding()

        (n0_r, r_n0) = connect(self.n0, r)
        (r_n1, n1_r) = connect(r, self.n1)

        n0_r.set_address('10.1.1.1/24')
        r_n0.set_address('10.1.1.2/24')
        r_n1.set_address('10.1.2.2/24')
        n1_r.set_address('10.1.2.1/24')

        self.n0.add_route('DEFAULT', n0_r)
        self.n1.add_route('DEFAULT', n1_r)

        status = self.n0.ping('10.1.2.1', verbose=False)

        self.assertTrue(status)

    def test_tcp_param(self):
        self.n0.configure_tcp_param('ecn', '1')
        ecn = self.n0.read_tcp_param('ecn')
        self.assertEqual(ecn, '1')

if __name__ == '__main__':
    unittest.main()
