# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

from ..topology import Address, topology
from ..configuration import Configuration
from . import run_tests
class Test():

    # TODO: Add feature to specify which stats to obtain; and from which qdisc and classes

    def __init__(self, name):
        """
        Create test

        :param name: name of test
        :type name: string
        """
        
        # TODO: Verify if name is string
        self.name = name

    def add_flow(self, source_node, destination_node, destination_address, start_time, stop_time, number_of_flows):
        """
        Add flow

        :param source_node: Source node of flow
        :type source_node: Node
        :param destination_node: Destination node of flow
        :type destination_node: Node
        :param destination_address: Destination address of flow
        :type destination_address: Address/string
        :param start_time: Time to start flow
        :type start_time: int
        :param stop_time: Time to stop flow
        :type stop_time: int
        :param number_of_flows: Number of flows
        :type number_of_flows: int
        """

        # Verify address passed by user
        if type(destination_address) is str:
            destination_address = Address(destination_address)

        # TODO: Verify if source_node and destination_node is actually a node
        Configuration.add_test(self.name, source_node.get_id(), destination_node.get_id(), destination_address.get_addr(with_subnet=False),
            start_time, stop_time, number_of_flows)

    def run(self):
        """
        Run the test
        """

        # Configuration.dump()
        run_tests.parse_config()
        

