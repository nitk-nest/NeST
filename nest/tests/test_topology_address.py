# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Test Address sub-module in topology"""

import unittest
from nest.topology.address import Address, Subnet

#pylint: disable=missing-docstring

class TestTopologyAddress(unittest.TestCase):

    def setUp(self):
        self.addr = '10.0.0.1/24'
        self.addr_without_subnet = '10.0.0.1'

        self.subnet_addr = '10.0.0.0/24'

    def test_get_addr(self):
        address = Address(self.addr)
        self.assertEqual(address.get_addr(), self.addr)
        self.assertEqual(address.get_addr(with_subnet=False), self.addr_without_subnet)

    def test_address_subnet(self):
        subnet_address = Address(self.subnet_addr)
        self.assertTrue(subnet_address.is_subnet())

        address = Address(self.addr)
        self.assertEqual(address.get_subnet(), self.subnet_addr)

    def test_subnet(self):
        subnet = Subnet(self.subnet_addr)
        self.assertEqual(subnet.get_next_addr().get_addr(), self.addr)

if __name__ == '__main__':
    unittest.main()
