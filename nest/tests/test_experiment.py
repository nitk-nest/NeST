# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Test APIs from topology sub-package"""

import unittest
from nest.topology import Node, connect
from nest.experiment import Experiment, Flow
from nest.clean_up import delete_namespaces
from nest.topology_map import TopologyMap
import nest.config as config

# pylint: disable=missing-docstring
# pylint: disable=invalid-name
class TestExperiment(unittest.TestCase):
    def test_experiment(self):
        n0 = Node("n0")
        n1 = Node("n1")
        r = Node("r")
        r.enable_ip_forwarding()

        (n0_r, r_n0) = connect(n0, r)
        (r_n1, n1_r) = connect(r, n1)

        n0_r.set_address("10.1.1.1/24")
        r_n0.set_address("10.1.1.2/24")
        r_n1.set_address("10.1.2.2/24")
        n1_r.set_address("10.1.2.1/24")

        n0.add_route("DEFAULT", n0_r)
        n1.add_route("DEFAULT", n1_r)

        n0_r.set_attributes("100mbit", "5ms")
        r_n0.set_attributes("100mbit", "5ms")

        r_n1.set_attributes("10mbit", "40ms", "pie")
        n1_r.set_attributes("10mbit", "40ms")

        exp = Experiment("test-experiment")
        flow = Flow(n0, n1, n1_r.address, 0, 5, 2)
        exp.add_tcp_flow(flow)

        exp.run()

    def test_experiment_udp(self):
        n0 = Node("n0")
        n1 = Node("n1")
        r = Node("r")
        r.enable_ip_forwarding()

        (n0_r, r_n0) = connect(n0, r)
        (r_n1, n1_r) = connect(r, n1)

        n0_r.set_address("10.1.1.1/24")
        r_n0.set_address("10.1.1.2/24")
        r_n1.set_address("10.1.2.2/24")
        n1_r.set_address("10.1.2.1/24")

        n0.add_route("DEFAULT", n0_r)
        n1.add_route("DEFAULT", n1_r)

        n0_r.set_attributes("100mbit", "5ms")
        r_n0.set_attributes("100mbit", "5ms")

        r_n1.set_attributes("10mbit", "40ms", "pie")
        n1_r.set_attributes("10mbit", "40ms")

        exp = Experiment("test-experiment-udp")
        flow = Flow(n0, n1, n1_r.address, 0, 5, 2)
        exp.add_udp_flow(flow)

        exp.run()

    def test_experiment_ipv6(self):
        # Test IPv6 with Duplicate Address Detection (DAD) disabled
        n0 = Node("n0")
        n1 = Node("n1")
        r = Node("r")
        r.enable_ip_forwarding()

        (n0_r, r_n0) = connect(n0, r)
        (r_n1, n1_r) = connect(r, n1)

        n0_r.set_address("10::1:1/122")
        r_n0.set_address("10::1:2/122")
        r_n1.set_address("10::2:2/122")
        n1_r.set_address("10::2:1/122")

        n0.add_route("DEFAULT", n0_r)
        n1.add_route("DEFAULT", n1_r)

        n0_r.set_attributes("100mbit", "5ms")
        r_n0.set_attributes("100mbit", "5ms")

        r_n1.set_attributes("10mbit", "40ms", "pie")
        n1_r.set_attributes("10mbit", "40ms")

        exp = Experiment("test-experiment-ipv6")
        flow = Flow(n0, n1, n1_r.address, 0, 5, 2)
        exp.add_tcp_flow(flow)

        exp.run()

    def test_experiment_ipv6_dad(self):
        # Test IPv6 with Duplicate Address Detection (DAD) enabled
        config.set_value("disable_dad", False)

        n0 = Node("n0")
        n1 = Node("n1")
        r = Node("r")
        r.enable_ip_forwarding()

        (n0_r, r_n0) = connect(n0, r)
        (r_n1, n1_r) = connect(r, n1)

        n0_r.set_address("10::1:1/122")
        r_n0.set_address("10::1:2/122")
        r_n1.set_address("10::2:2/122")
        n1_r.set_address("10::2:1/122")

        n0.add_route("DEFAULT", n0_r)
        n1.add_route("DEFAULT", n1_r)

        n0_r.set_attributes("100mbit", "5ms")
        r_n0.set_attributes("100mbit", "5ms")

        r_n1.set_attributes("10mbit", "40ms", "pie")
        n1_r.set_attributes("10mbit", "40ms")

        exp = Experiment("test-experiment-ipv6-dad")
        flow = Flow(n0, n1, n1_r.address, 0, 5, 2)
        exp.add_tcp_flow(flow)

        exp.run()

        # Resetting disable_dad in config
        config.set_value("disable_dad", True)

    def tearDown(self):
        delete_namespaces()
        TopologyMap.delete_all_mapping()


if __name__ == "__main__":
    unittest.main()
