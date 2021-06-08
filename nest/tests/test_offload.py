# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal
"""Test APIs from topology sub-package"""

import unittest
import subprocess
from nest.topology_map import TopologyMap
from nest.topology import Node, connect
from nest.clean_up import delete_namespaces

# pylint: disable=invalid-name
# pylint: disable=missing-docstring
# pylint: disable=consider-using-with


class TestOffloads(unittest.TestCase):
    def tearDown(self):
        delete_namespaces()
        TopologyMap.delete_all_mapping()

    def test_enable_offload(self):
        n2 = Node("n2")
        n1 = Node("n1")

        (n1_n2, n2_n1) = connect(n1, n2)

        # Enable TSO offload on n1_n2 interface
        n1_n2.enable_offload("tso")
        with n1:
            proc = subprocess.Popen(
                f"ip netns exec {n1.id}  ethtool -k {n1_n2.id}",
                shell=True,
                stdout=subprocess.PIPE,
            )
            (output, _) = proc.communicate()
            self.assertTrue("tcp-segmentation-offload: on" in output.decode())

        # Enable offloads GSO, GRO on n2_n1 interface
        n2_n1.enable_offload(["gso", "gro"])
        with n2:
            proc = subprocess.Popen(
                f"ip netns exec {n2.id}  ethtool -k {n2_n1.id}",
                shell=True,
                stdout=subprocess.PIPE,
            )
            (output, _) = proc.communicate()
            self.assertTrue("generic-segmentation-offload: on" in output.decode())
            self.assertTrue("generic-receive-offload: on" in output.decode())

    def test_disable_offload(self):
        n2 = Node("n2")
        n1 = Node("n1")

        (n1_n2, n2_n1) = connect(n1, n2)

        # Disable TSO offload on n1_n2 interface
        n1_n2.disable_offload("tso")
        with n1:
            proc = subprocess.Popen(
                f"ip netns exec {n1.id}  ethtool -k {n1_n2.id}",
                shell=True,
                stdout=subprocess.PIPE,
            )
            (output, _) = proc.communicate()
            self.assertTrue("tcp-segmentation-offload: off" in output.decode())

        # Disable offloads GSO, GRO on n2_n1 interface
        n2_n1.disable_offload(["gso", "gro"])
        with n2:
            proc = subprocess.Popen(
                f"ip netns exec {n2.id}  ethtool -k {n2_n1.id}",
                shell=True,
                stdout=subprocess.PIPE,
            )
            (output, _) = proc.communicate()
            self.assertTrue("generic-segmentation-offload: off" in output.decode())
            self.assertTrue("generic-receive-offload: off" in output.decode())


if __name__ == "__main__":
    unittest.main()
