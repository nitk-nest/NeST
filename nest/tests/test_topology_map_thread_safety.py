# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""Test thread-safety of the TopologyMap"""

import unittest
from threading import Thread
from nest.topology import connect, Node
from nest.topology_map import TopologyMap

# pylint: disable=missing-docstring
# pylint: disable=too-many-instance-attributes
# pylint: disable=attribute-defined-outside-init


class TestThreadSafety(unittest.TestCase):
    def _add_node(self, node_id):
        # Work done by a thread
        node = Node("n" + str(node_id))
        self.nodes.append(node)

    def _add_and_connect(self, id1, id2):
        # Work done by a thread
        node_1 = Node("n" + str(id1))
        node_2 = Node("n" + str(id2))
        self.nodes.extend([node_1, node_2])

        (eth0, eth1) = connect(node_1, node_2)
        self.interfaces.extend([eth0, eth1])

    def test_thread_safety_of_nodes(self):
        # set up
        num_of_threads = 10

        self.threads = []
        self.nodes = []

        # Create the threads
        for i in range(0, num_of_threads):
            a_thread = Thread(target=self._add_node, args=(i,))
            self.threads.append(a_thread)

        # Start the threads
        for thread in self.threads:
            thread.start()

        # Join the threads
        for thread in self.threads:
            thread.join()

        # Validate
        for node in self.nodes:
            self.assertEqual(TopologyMap.get_node(node.id).name, node.name)

        TopologyMap.delete_all_mapping()

    def test_thread_safety_of_all(self):
        # set up
        num_of_threads = 10

        self.threads = []
        self.nodes = []
        self.interfaces = []
        if num_of_threads % 2 == 1:
            num_of_threads = num_of_threads + 1

        # Create the threads
        for i in range(0, num_of_threads, 2):
            a_thread = Thread(
                target=self._add_and_connect,
                args=(
                    i,
                    i + 1,
                ),
            )
            self.threads.append(a_thread)

        # Start the threads
        for thread in self.threads:
            thread.start()

        # Join the threads
        for thread in self.threads:
            thread.join()

        # Validate
        for node in self.nodes:
            self.assertEqual(TopologyMap.get_node(node.id).name, node.name)

        for interface in self.interfaces:
            self.assertEqual(
                TopologyMap.get_device(interface.node_id, interface.id).name,
                interface.name,
            )

        TopologyMap.delete_all_mapping()


if __name__ == "__main__":
    unittest.main()
