# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Test Address sub-module in topology"""

import unittest
from nest.topology.address import Address, Subnet

# pylint: disable=missing-docstring


class TestTopologyAddress(unittest.TestCase):
    def setUp(self):
        self.addr = "10.0.0.1/24"
        self.addr_without_subnet = "10.0.0.1"
        self.default_addr = "DEFAULT"
        self.subnet_addr = "10.0.0.0/24"

    def test_get_addr(self):
        address = Address(self.addr)
        self.assertEqual(address.get_addr(), self.addr)
        self.assertEqual(address.get_addr(with_subnet=False), self.addr_without_subnet)

        with self.assertRaises(ValueError):
            Address("10.0.0.0a/24")  # invalid character 'a'

        with self.assertRaises(ValueError):
            Address("10.0asdfasf")  # invalid string

        with self.assertRaises(ValueError):
            Address("10.0.0./24")  # invalid ./

        with self.assertRaises(ValueError):
            Address("10.0.0.2000/24")  # invalid mask 2000

        with self.assertRaises(ValueError):
            Address("256.0.0.0/24")  # invalid mask 256

    def test_address_subnet(self):
        subnet_address = Address(self.subnet_addr)
        self.assertTrue(subnet_address.is_subnet())

        address = Address(self.addr)
        self.assertEqual(address.get_subnet(), self.subnet_addr)

        with self.assertRaises(ValueError):
            Subnet("10.0.0.1/24")  # 10.0.0.1/24 is not a subnet

    def test_subnet(self):
        subnet = Subnet(self.subnet_addr)
        self.assertEqual(subnet.get_next_addr().get_addr(), "10.0.0.1/24")
        self.assertEqual(subnet.get_next_addr().get_addr(), "10.0.0.2/24")
        self.assertEqual(subnet.get_next_addr().get_addr(), "10.0.0.3/24")

        with self.assertRaises(ValueError):
            Subnet("10.0.0.1/24").get_next_addr()

        with self.assertRaises(ValueError):
            Subnet(
                "10.0.0.0/32"
            ).get_next_addr()  # no next address possible as the mask is 32

    def test_default(self):
        def_addr = Address("DEFAULT")
        self.assertEqual("default", def_addr.get_addr())
        self.assertEqual(False, def_addr.is_subnet())

        with self.assertRaises(Exception):
            def_addr.get_subnet()  # no subnet for default

        with self.assertRaises(Exception):
            Subnet("DEFAULT")  # DEFAULT cannot be a subnet


if __name__ == "__main__":
    unittest.main()
