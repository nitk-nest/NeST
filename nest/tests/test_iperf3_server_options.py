# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""Test APIs for iperf3 server options"""

import json
import os
import unittest
from nest.experiment.pack import Pack

from nest.topology import Node, connect, Switch
from nest.clean_up import delete_namespaces
from nest.topology_map import TopologyMap
from nest.experiment import Experiment, Flow

# from nest import config
# config.set_value("log_level", "TRACE")


# pylint: disable=unused-variable
def search_file(filename):
    """
    Search file in current directory

    Parameter:
    ----------
    filename: str
        file name to search

    Returns:
        if found return file else False
    """
    folder_name = Pack.FOLDER
    folder_path = os.path.join(os.getcwd(), folder_name)
    file_name = filename
    if os.path.exists(folder_path):
        for root, directory, files in os.walk(folder_path):
            if file_name in files:
                filepath = os.path.join(folder_path, file_name)
                with open(filepath, "r") as file:
                    result = json.loads(file.read())
                    file.close()
                return result
    return False


# pylint: disable=missing-docstring
# pylint: disable=invalid-name, unused-variable, redefined-builtin
# pylint: disable=too-many-instance-attributes,  too-many-nested-blocks
class TestIperf3Options(unittest.TestCase):
    def tearDown(self):
        delete_namespaces()
        TopologyMap.delete_all_mapping()

    def setUp(self):
        # Network setup to test different iperf3 options
        # Local Area Networks (LANs) connected directly to
        # each other. LAN-1 consists three hosts `h1` to `h3` connected to switch `s1`,
        # and LAN-2 consists three hosts `h4` to `h6` connected to switch `s2`.
        # Switches `s1` and `s2` are connected to each other.

        #########################################################
        #                    Network Topology                   #
        #           LAN-1                      LAN-2            #
        #   h1 ---------------            ---------------- h4   #
        #                     \         /                       #
        #   h2 --------------- s1 ---- s2 ---------------- h5   #
        #                     /         \                       #
        #   h3 ---------------            ---------------- h6   #
        #             <------ 100mbit, 1ms ------>              #
        #                                                       #
        #########################################################

        # Create six hosts `h1` to `h6`, and two switches `s1` and `s2`
        self.h1 = Node("h1")
        self.h2 = Node("h2")
        self.h3 = Node("h3")
        self.h4 = Node("h4")
        self.h5 = Node("h5")
        self.h6 = Node("h6")
        self.s1 = Switch("s1")
        self.s2 = Switch("s2")

        # Create LAN-1: Connect hosts `h1`, `h2` and `h3` to switch `s1`
        # `eth1` to `eth3` are the interfaces at `h1` to `h3`, respectively.
        # `ets1a` is the first interface at `s1` which connects it with `h1`
        # `ets1b` is the second interface at `s1` which connects it with `h2`
        # `ets1c` is the third interface at `s1` which connects it with `h3`
        (eth1, ets1a) = connect(self.h1, self.s1)
        (eth2, ets1b) = connect(self.h2, self.s1)
        (eth3, ets1c) = connect(self.h3, self.s1)

        # Create LAN-2: Connect hosts `h4`, `h5` and `h6` to switch `s2`
        # `eth4` to `eth6` are the interfaces at `h4` to `h6`, respectively.
        # `ets2a` is the first interface at `s2` which connects it with `h4`
        # `ets2b` is the second interface at `s2` which connects it with `h5`
        # `ets2c` is the third interface at `s2` which connects it with `h6`
        (eth4, ets2a) = connect(self.h4, self.s2)
        (eth5, ets2b) = connect(self.h5, self.s2)
        (eth6, ets2c) = connect(self.h6, self.s2)

        # Connect switches `s1` and `s2`
        # `ets1d` is the fourth interface at `s1` which connects it with `s2`
        # `ets2d` is the fourth interface at `s2` which connects it with `s1`
        (ets1d, ets2d) = connect(self.s1, self.s2)

        # Assign IPv4 addresses to all the interfaces.
        # We assume that the IPv4 address of this network is `192.168.1.0/24`.
        # Note: IP addresses should not be assigned to the interfaces on the switches.
        eth1.set_address("192.168.1.1/24")
        eth2.set_address("192.168.1.2/24")
        eth3.set_address("192.168.1.3/24")
        eth4.set_address("192.168.1.4/24")
        eth5.set_address("192.168.1.5/24")
        eth6.set_address("192.168.1.6/24")

        # Set the link attributes
        eth1.set_attributes("100mbit", "1ms")
        eth2.set_attributes("100mbit", "1ms")
        eth3.set_attributes("100mbit", "1ms")
        eth4.set_attributes("100mbit", "1ms")
        eth5.set_attributes("100mbit", "1ms")
        eth6.set_attributes("100mbit", "1ms")

        # Assign  source, Destination, start time, end time and number of
        # parallel flows to each udp flows
        self.flow_udp_1 = Flow(self.h1, self.h4, eth4.get_address(), 0, 5, 1)
        self.flow_udp_2 = Flow(self.h2, self.h4, eth4.get_address(), 5, 15, 1)

    def test_set_dport(self):

        # iperf3_server_options API is used to configure iperf3 server options
        portno = 12345
        self.flow_udp_1.iperf3_server_options(port_no=portno)

        exp = Experiment("flow")
        exp.add_udp_flow(self.flow_udp_1)
        exp.run()

        exp_output = search_file("iperf3Server.json")
        dst_name = self.h4.name
        src_ip = "192.168.1.1"
        status = False
        if exp_output:
            for dict in exp_output[dst_name]:
                if src_ip in dict:
                    for dst_port in dict[src_ip]:
                        if portno == int(dst_port):
                            status = True

        self.assertTrue(status)

    def test_set_interval(self):

        # iperf3_server_options API is used to configure iperf3 server options
        interval = 0.4
        self.flow_udp_1.iperf3_server_options(interval=interval)

        exp = Experiment("flow")
        exp.add_udp_flow(self.flow_udp_1)
        exp.run()

        exp_output = search_file("iperf3Server.json")
        dst_name = self.h4.name
        src_ip = "192.168.1.1"
        status = False
        if exp_output:
            for dict in exp_output[dst_name]:
                if src_ip in dict:
                    interval = []
                    for dst_port in dict[src_ip]:
                        for dict1 in dict[src_ip][dst_port]:
                            if "duration" in dict1:
                                interval.append(float(dict1["duration"]))
                    average = sum(interval) / len(interval)
                    if interval == round(average, 1):
                        status = True

        self.assertTrue(status)


if __name__ == "__main__":
    unittest.main()
