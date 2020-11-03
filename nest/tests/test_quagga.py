# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Test APIs from routing sub-package"""

import unittest
from nest.topology import Node, connect
from nest.routing.routing_helper import RoutingHelper
from nest.clean_up import delete_namespaces

#pylint: disable=missing-docstring

class TestQuagga(unittest.TestCase):

    # pylint: disable=invalid-name
    @classmethod
    def setUpClass(cls):
        cls.n0 = Node('n0')
        cls.n1 = Node('n1')
        cls.r0 = Node('r0')
        cls.r1 = Node('r1')
        cls.r0.enable_ip_forwarding()
        cls.r1.enable_ip_forwarding()

        ### Create interfaces and connect nodes and routers ###

        (eth_p1r1, eth_r1p1) = connect(cls.n0, cls.r0, 'eth-n1r1-0', 'eth-r1n1-0')
        (eth_r1r2, eth_r2r1) = connect(cls.r0, cls.r1, 'eth-r1r2-0', 'eth-r2r1-0')
        (eth_r2p2, eth_p2r2) = connect(cls.r1, cls.n1, 'eth-r2n2-0', 'eth-n2r2-0')

        ### Assign addresses to interfaces ###

        eth_p1r1.set_address('10.0.1.1/24')
        eth_r1p1.set_address('10.0.1.2/24')

        eth_r1r2.set_address('10.0.2.2/24')
        eth_r2r1.set_address('10.0.2.3/24')

        eth_r2p2.set_address('10.0.3.3/24')
        eth_p2r2.set_address('10.0.3.4/24')

    @classmethod
    def tearDownClass(cls):
        delete_namespaces()


    def test_routing_helper(self):

        RoutingHelper('rip').populate_routing_tables()

        status = self.n0.ping('10.0.3.4', verbose=False)
        self.assertTrue(status)

        status = self.n1.ping('10.0.1.1', verbose=False)
        self.assertTrue(status)


if __name__ == '__main__':
    unittest.main()
