# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Test Address sub-module in topology"""

import unittest
from nest.topology.address import Address, Subnet

# pylint: disable=missing-docstring


class TestTopologyAddress(unittest.TestCase):
    def setUp(self):
        self.addr = "2001:1:1:1443::1/64"
        self.addr_without_subnet = "2001:1:1:1443::1"
        self.default_addr = "DEFAULT"
        self.subnet_addr = "2001:1:1:1443::/64"

    def test_get_addr(self):
        address = Address(self.addr)
        self.assertEqual(address.get_addr(), self.addr)
        self.assertEqual(address.get_addr(with_subnet=False), self.addr_without_subnet)

        with self.assertRaises(ValueError):
            Address("2001:1:1:1443::g/64")  # invalid character 'g'

        with self.assertRaises(ValueError):
            Address("2001:1asdfasf")  # invalid string

        with self.assertRaises(ValueError):
            Address("2001:1:1:1443:::/64")  # invalid :::

        with self.assertRaises(ValueError):
            Address(":/64")  # invalid :

        with self.assertRaises(ValueError):
            Address("2001:1:1:1443::g000")  # invalid mask g000

        with self.assertRaises(ValueError):
            Address("gggg:1:1:1443::")  # invalid mask gggg

    def test_address_subnet(self):
        subnet_address = Address(self.subnet_addr)
        self.assertTrue(subnet_address.is_subnet())

        address = Address(self.addr)
        self.assertEqual(address.get_subnet(), self.subnet_addr)

        with self.assertRaises(ValueError):
            Subnet("2001:1:1:1443::1/64")  # 2001:1:1:1443::1/64 is not a subnet

    def test_subnet(self):
        subnet = Subnet(self.subnet_addr)

        self.assertEqual(subnet.get_next_addr().get_addr(), "2001:1:1:1443::1/64")
        self.assertEqual(subnet.get_next_addr().get_addr(), "2001:1:1:1443::2/64")
        self.assertEqual(subnet.get_next_addr().get_addr(), "2001:1:1:1443::3/64")

        with self.assertRaises(ValueError):
            Subnet("2001:1:1:1443::1/64").get_next_addr()

        with self.assertRaises(ValueError):
            Subnet(
                "2001:1:1:1443::/128"
            ).get_next_addr()  # no next subnet as the mask is 128

    def test_default(self):
        def_addr = Address("DEFAULT")

        with self.assertRaises(ValueError):
            def_addr.is_ipv6()  # raises error since 'default' is not a valid IPv4 or IPv6 address

        self.assertEqual("default", def_addr.get_addr())
        self.assertEqual(False, def_addr.is_subnet())

        with self.assertRaises(Exception):
            def_addr.get_subnet()  # no subnet for default

        with self.assertRaises(Exception):
            Subnet("DEFAULT")  # DEFAULT cannot be a subnet


if __name__ == "__main__":
    unittest.main()
