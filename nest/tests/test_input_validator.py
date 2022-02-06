# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""Test APIs from input_validator sub-package"""

import unittest
from typing import List
from nest.input_validator import input_validator
from nest.topology import Node, Address

# pylint: disable=missing-docstring


@input_validator
def samplemethod(arg1: int, arg2: str):
    assert isinstance(arg1, int)
    assert isinstance(arg2, str)


@input_validator
def samplemethod2(node: Node, address: Address):
    assert isinstance(node, Node)
    assert isinstance(address, Address)


@input_validator
def samplemethod3(interfaces: List[Node], address: Address = None):
    assert isinstance(interfaces, list)
    assert address is None


class TestInputValidator(unittest.TestCase):
    def test_expected_type(self):
        samplemethod(1, "2")

        with self.assertRaises(TypeError) as ex:
            samplemethod("1", 2)

        self.assertEqual(
            str(ex.exception),
            "Expected type of argument 'arg1' in method 'samplemethod' "
            "is <class 'int'>. But got input '1' of type <class 'str'>",
        )

        with self.assertRaises(TypeError) as ex:
            samplemethod(1, 2)

        self.assertEqual(
            str(ex.exception),
            "Expected type of argument 'arg2' in method 'samplemethod' "
            "is <class 'str'>. But got input '2' of type <class 'int'>",
        )

    def test_type_casting(self):
        samplemethod2(Node("n1"), Address("10.0.0.1/24"))

        samplemethod2(Node("n2"), "10.0.0.1/24")

        with self.assertRaises(TypeError) as ex:
            samplemethod2("n3", "10.0.0.1/24")

        self.assertEqual(
            str(ex.exception),
            "Expected type of argument 'node' in method 'samplemethod2' "
            "is <class 'nest.topology.node.Node'>. But got input 'n3' of type <class 'str'>",
        )

        with self.assertRaises(TypeError) as ex:
            samplemethod2(Node("n4"), "10.0.0.1/244")

        self.assertEqual(
            str(ex.exception),
            "For argument 'address' in method 'samplemethod2', "
            "converting '10.0.0.1/244' to type Address failed.\n"
            "Please see the previous exception to know why the conversion failed.",
        )

    def test_optional_and_list_field(self):
        samplemethod3([Node("h1"), Node("h2")])

        with self.assertRaises(TypeError) as ex:
            samplemethod3(Node("h3"))

        self.assertEqual(
            str(ex.exception),
            "Expected type of argument 'interfaces' in method 'samplemethod3' "
            "is List. But got input 'Node('h3')' of type <class 'nest.topology.node.Node'>",
        )


if __name__ == "__main__":
    unittest.main()
