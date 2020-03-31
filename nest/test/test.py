# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# User API to setup and run tests
# on a given topology

from ..topology import Address, Node, Router, Interface
from ..configuration import Configuration
from . import run_tests
from .. import error_handling

class Flow():
    """
    Defines a flow in the topology
    """

    def __init__(self, source_node, destination_node, destination_address, start_time, stop_time, number_of_flows):
        """
        'Flow' object in the topology

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

        # Verify types of all args
        error_handling.type_verify('source_node', source_node, 'Namespace', [Node, Router])
        error_handling.type_verify('destination_node', destination_node, 'Namespace', [Node, Router]) 
        # Verify address passed by user
        if type(destination_address) is str:
            destination_address = Address(destination_address)
        error_handling.type_verify('start_time', start_time, 'int', int)
        error_handling.type_verify('stop_time', stop_time, 'int', int)
        error_handling.type_verify('number_of_flows', number_of_flows, 'int', int)

        self.source_node = source_node
        self.destination_node = destination_node
        self.destination_address = destination_address
        self.start_time = start_time
        self.stop_time = stop_time
        self.number_of_flows = number_of_flows


    def _get_props(self):
        """
        Get flow properties.
        NOTE: To be used internelly
        """

        return [self.source_node.get_id(), self.destination_node.get_id(),
                self.destination_address.get_addr(with_subnet=False), 
                self.start_time, self.stop_time, self.number_of_flows]

class Test():

    # List of node and qdisc stats
    # the API supports
    node_stats = ['cwnd', 'rtt']
    qdisc_stats = ['qlen', 'latency']

    def __init__(self, name):
        """
        Create test

        :param name: name of test
        :type name: string
        """
        
        error_handling.type_verify('Name', name, 'string', str)

        self.name = name
        self.flows = []
        self.node_stats = []
        self.qdisc_stats = []

    def add_flow(self, flows):
        """
        Add flow to test

        :param flows: Add flow to test
        :type flows: list(Flow)
        """

        if type(flows) is list:
            for flow in flows:
                error_handling.type_verify('Flow', flow, 'Flow', Flow)
                self.flows.append(flow)
        else:
            flow = flows
            error_handling.type_verify('Flow', flow, 'Flow', Flow)
            self.flows.append(flow)

    def require_node_stats(self, node, stats):
        """
        Stats to be obtained from node
        in the tests

        :param node: Node from which stats are to be obtained
        :type node: Node
        :param stats: Stats required
        :type stats: list(string)
        """

        # TODO: Leads to rewrite if the function is called
        # twice with same 'node'

        error_handling.type_verify('Node', node, 'Node', Node)
        error_handling.type_verify('Stats', stats, 'list', list)

        for stat in stats:
            if stat not in Test.node_stats:
                raise ValueError('{} is not a valid Node property.'.format(stat))

        self.node_stats.append({
            'id': node.get_id(),
            'stats': stats
        })

    def require_qdisc_stats(self, interface, stats):
        """
        Stats to be obtained from qdisc in interface

        :param interface: Interface containing the qdisc
        :type interface: Interface
        :param stats: Stats required
        :type stats: list(string)
        """

        # TODO: Leads to rewrite if the function is called
        # twice with same 'interface'

        error_handling.type_verify('Interface', interface, 'Interface', Interface)
        error_handling.type_verify('Stats', stats, 'list', list)

        for stat in stats:
            if stat not in Test.qdisc_stats:
                raise ValueError('{} is not a valid Queue property.'.format(stat))

        if interface.get_qdisc() is None:
            raise ValueError('Given interface hasn\'t been assigned any qdisc.')

        self.qdisc_stats.append({
            'ns_id': interface.get_namespace(),
            'int_id': interface.get_id(),
            'qdisc_handle': interface.get_qdisc().handle,
            'stats': stats
        })

    def get_flows(self):
        """
        Getter for flows in test
        """

        return self.flows

    def run(self):
        """
        Run the test
        """

        # Configuration.dump()
        print('Running test ' + self.name)
        run_tests.parse_config(self) 
