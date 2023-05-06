# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal
"""Test APIs from topology packet operations"""

import unittest
from contextlib import redirect_stdout
import io
import os
from os.path import exists
from nest.topology import Node, connect
from nest.clean_up import delete_namespaces
from nest.topology_map import TopologyMap


# pylint: disable=invalid-name
# pylint: disable=missing-docstring


class TestTopologyPacketOps(unittest.TestCase):
    def setUp(self):
        self.n0 = Node("n0")
        self.n1 = Node("n1")

        (self.n0_n1, self.n1_n0) = connect(self.n0, self.n1)

        self.n0_n1.set_address("10.0.0.1/24")
        self.n1_n0.set_address("10.0.0.2/24")

    def parse_ping_output(self):
        # TODO: Optimize the below function using regex

        f = io.StringIO()
        checker = False
        with redirect_stdout(f):
            self.n0.ping("10.0.0.2", packets=50)
        out = f.getvalue()
        pointer = out.find(
            "packet loss"
        )  # pointer to the initial character of string "packet loss".
        pointer = pointer - 3  # it will point to the last digit of packet loss %.
        num = 0
        while (
            out[pointer] != " "
        ):  # it is tracing from last digit to the first digit to get actual % loss number.
            num = int(out[pointer]) * 10 + num
            pointer = pointer - 1
        if num > 0:
            checker = True
        self.assertTrue(checker, "packets are not being corrupted")

    def test_packet_loss_state(self):
        self.n0_n1.set_packet_loss_state("20%", "4%", "5%", "4%", "3%", True)
        status = self.n0.ping("10.0.0.2")

        self.assertTrue(status)

    def test_packet_loss_gemodel(self):
        self.n0_n1.set_packet_loss_gemodel("10%", "4%", "5%", "4%", True)
        status = self.n0.ping("10.0.0.2")

        self.assertTrue(status)

    # Add rate in percent to get packet duplicated.
    def test_packet_duplication(self):
        # Add rate in percent to get packet duplicated.
        self.n0_n1.set_packet_duplication("50%")

        f = io.StringIO()
        checker = False
        with redirect_stdout(f):
            self.n0.ping("10.0.0.2", packets=15)
        out = f.getvalue()
        if "duplicates" in out:
            checker = True
        self.assertTrue(checker, "Packets are not being duplicated")

    def test_packet_corruption(self):
        self.n0_n1.set_packet_corruption("75%", "50%")
        self.parse_ping_output()

    def test_packet_reordering(self):
        self.n0_n1.set_attributes("10mbit", "10ms")
        self.n1_n0.set_attributes("10mbit", "5ms")

        self.n0_n1.set_packet_reordering("10ms", "25%", gap=5)

        self.n0.ping("10.0.0.2", packets=1)  # build ARP table before preload is used.
        status = self.n0.ping("10.0.0.2", preload=10, packets=10)

        self.assertTrue(status)

    def test_delay_distribution(self):
        (n0_n1, n1_n0) = connect(self.n0, self.n1)

        n0_n1.set_attributes("10mbit", "10ms")
        n1_n0.set_attributes("10mbit", "5ms")

        n0_n1.set_delay_distribution("100ms", "10ms", "normal")

        status = self.n0.ping("10.0.0.2", packets=10)

        self.assertTrue(status)

    def test_packet_capture(self):
        self.n0_n1.set_attributes("10mbit", "10ms")
        current_dir = os.getcwd()
        initial_status = exists(f"{current_dir}/packet_capture/packet_capture.pcap")
        self.n1.capture_packets(
            interface=self.n1_n0, packet_count=10, output_file="packet_capture.pcap"
        )
        self.n0.ping("10.0.0.2", packets=10)

        status = exists(f"{current_dir}/packet_capture/packet_capture.pcap")
        self.assertTrue(status)
        if initial_status is False and status is True:
            os.remove(f"{current_dir}/packet_capture/packet_capture.pcap")

    def tearDown(self):
        delete_namespaces()
        TopologyMap.delete_all_mapping()


if __name__ == "__main__":
    unittest.main()
