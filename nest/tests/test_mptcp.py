# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Test APIs from topology sub-package"""

import os
import json
import shutil
import unittest
from nest.topology import Node, connect
from nest.experiment import Experiment, Flow
from nest.clean_up import delete_namespaces
from nest.topology_map import TopologyMap


# pylint: disable=missing-docstring
# pylint: disable=invalid-name
# pylint: disable=too-many-locals
class TestMPTCP(unittest.TestCase):
    def setUp(self):
        # Create two MPTCP enabled hosts `h1` and `h2`
        h1 = Node("h1")
        h2 = Node("h2")

        # Connect `h1` to `h2`
        # `eth1a` and `eth2a` are the interfaces at `h1` and `h2`, respectively, for 1st connection.
        # `eth1b` and `eth2b` are the interfaces at `h1` and `h2`, respectively, for 2nd connection.
        (eth1a, eth2a) = connect(h1, h2)
        (eth1b, eth2b) = connect(h1, h2)

        # Assign IPv4 addresses to all the interfaces.
        eth1a.set_address("10.10.0.1/24")
        eth2a.set_address("10.10.0.2/24")
        eth1b.set_address("192.168.0.1/24")
        eth2b.set_address("192.168.0.2/24")

        # Set the link attributes: `h1` <--> `h2`
        eth1a.set_attributes("10mbit", "5ms")
        eth2a.set_attributes("10mbit", "5ms")
        eth1b.set_attributes("5mbit", "10ms")
        eth2b.set_attributes("5mbit", "10ms")

        h1.set_mptcp_parameters(1, 1)
        h2.set_mptcp_parameters(1, 1)

        eth1b.enable_mptcp_endpoint(["subflow"])
        eth2b.enable_mptcp_endpoint(["signal"])

        self.exp = Experiment("test-experiment-mptcp")
        flow = Flow(
            h1, h2, eth2a.get_address(), 0, 20, 1, source_address=eth1a.get_address()
        )
        self.exp.add_mptcp_flow(flow)
        self.exp.run()

    def test_mptcp(self):
        for directory in sorted(os.listdir("./")):
            if self.exp.name in directory:
                # pylint: disable=attribute-defined-outside-init
                self.experiment_directory = os.path.abspath(directory)

        self.assertIn("netperf.json", os.listdir(self.experiment_directory))

        with open(os.path.join(self.experiment_directory, "netperf.json"), "r") as f:
            experiment_data = json.load(f)["h1"][0]

            rate_counter = 0
            rate_sum = 0.0
            for obj in list(experiment_data.values())[0][11:]:
                rate_sum += float(obj["sending_rate"])
                rate_counter += 1

            self.assertTrue(
                rate_sum / rate_counter > 10, "MPTCP doesn't seem to be working!"
            )

    def tearDown(self):
        delete_namespaces()
        TopologyMap.delete_all_mapping()
        shutil.rmtree(self.experiment_directory)


if __name__ == "__main__":
    unittest.main()
