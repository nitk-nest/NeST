# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# User API to setup and run experiments
# on a given topology

import copy
from ..topology import Address, Node, Router, Interface
from ..topology_map import TopologyMap
from .run_exp import run_experiment
from .. import error_handling

class Flow():
    """
    Defines a flow in the topology
    """

    def __init__(self, source_node, destination_node, destination_address, start_time, stop_time, 
            number_of_flows):
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

        self.set_source_node(source_node)
        self.set_destination_node(destination_node)
        self.set_destination_address(destination_address)
        self.set_start_time(start_time)
        self.set_stop_time(stop_time)
        self.set_number_of_flows(number_of_flows)
        self.options = None

    def set_source_node(self, source_node):
        """
        Setter for source node

        :param source_node: Source node of flow
        :type source_node: Node
        """
         
        error_handling.type_verify('source_node', source_node, 'Namespace', [Node, Router])
        self.source_node = source_node

    def set_destination_node(self, destination_node):
        """
        Setter for destination node of flow

        :param destination_node: Destination node of flow
        :type destination_node: Node
        """

        error_handling.type_verify('destination_node', destination_node, 'Namespace', [Node, Router]) 
        self.destination_node = destination_node
    
    def set_destination_address(self, destination_address):
        """
        Setter for destination address of flow

        :param destination_address: Destination address of flow
        :type destination_address: Address/string
        """

        if type(destination_address) is str:
            destination_address = Address(destination_address)
        self.destination_address = destination_address

    def set_start_time(self, start_time):
        """
        Setter for start time of flow

        :param start_time: Time to start flow
        :type start_time: int
        """

        error_handling.type_verify('start_time', start_time, 'int', int)
        self.start_time = start_time

    def set_stop_time(self, stop_time):
        """
        Setter for stop time of flow

        :param stop_time: Time to stop flow
        :type stop_time: int
        """

        error_handling.type_verify('stop_time', stop_time, 'int', int)
        self.stop_time = stop_time

    def set_number_of_flows(self, number_of_flows):
        """
        Setter for number of flows

        :param number_of_flows: Number of flows
        :type number_of_flows: int
        """

        error_handling.type_verify('number_of_flows', number_of_flows, 'int', int)
        self.number_of_flows = number_of_flows

    def _set_options(self, options):
        """
        Setter for flow options

        :param options: Flow options
        :type options: dict
        """
        
        self.options = options


    def get_source_node(self):
        """
        Getter for source node of flow
        """

        return self.source_node

    def get_destination_node(self):
        """
        Getter for destination node of flow
        """

        return self.destination_node

    def get_destination_address(self):
        """
        Getter for destination address of flow
        """

        return self.destination_address

    def get_start_time(self):
        """
        Getter for start time of flow
        """

        return self.start_time

    def get_stop_time(self):
        """
        Getter for stop time of flow
        """

        return self.stop_time

    def get_number_of_flows(self):
        """
        Getter for number of flows
        """

        return self.number_of_flows

    def _get_props(self):
        """
        Get flow properties.
        NOTE: To be used internally
        """

        return [self.source_node.get_id(), self.destination_node.get_id(),
                self.destination_address.get_addr(with_subnet=False), 
                self.start_time, self.stop_time, self.number_of_flows, self.options]

class Experiment():

    # List of node and qdisc stats
    # the API supports
    node_stats = ['cwnd', 'rtt']
    qdisc_stats = ['qlen', 'latency']

    def __init__(self, name):
        """
        Create experiment

        :param name: name of experiment
        :type name: string
        """
        
        error_handling.type_verify('Name', name, 'string', str)

        self.name = name
        self.flows = []
        self.node_stats = []
        self.qdisc_stats = []

    def add_flow(self, flow):
        """
        Add flow to experiment
        By default, the flow is assumed to be
        TCP with cubic congestion algorithm

        :param flow: Add flow to experiment
        :type flow: flow
        """

        error_handling.type_verify('Flow', flow, 'Flow', Flow)
        self.flows.append(copy.deepcopy(flow))

    def add_tcp_flow(self, flow, congestion_algorithm='cubic'):
        """
        Add TCP flow to experiment

        :param flow: Flow to be added to experiment
        :type flow: Flow
        :param congestion_algorithm: TCP congestion algorithm
        :type congestion_algorithm: string
        """

        # TODO: Verify congestion algorithm
        
        options = {
            'protocol' : 'TCP',
            'cong_algo': congestion_algorithm 
        }

        flow._set_options(options)
        self.add_flow(flow)

    def add_udp_flow(self, flow):
        """
        Add UDP flow to experiment

        :param flow: Flow to be added to experiment
        :type flow: Flow
        """
        
        options = {
            'protocol' : 'UDP',
        }

        flow._set_options(options)
        self.add_flow(flow)

    def require_node_stats(self, node, stats=''):
        """
        Stats to be obtained from node
        in the experiment

        :param node: Node from which stats are to be obtained
        :type node: Node
        :param stats: Stats required
        :type stats: list(string)
        """

        # TODO: Leads to rewrite if the function is called
        # twice with same 'node'

        # error_handling.type_verify('Node', node, 'Node', Node)
        # error_handling.type_verify('Stats', stats, 'list', list)

        # for stat in stats:
        #     if stat not in Experiment.node_stats:
        #         raise ValueError('{} is not a valid Node property.'.format(stat))

        self.node_stats.append({
            'id': node.get_id(),
            'stats': stats
        })

    def require_qdisc_stats(self, interface, stats=''):
        """
        Stats to be obtained from qdisc in interface

        :param interface: Interface containing the qdisc
        :type interface: Interface
        :param stats: Stats required
        :type stats: list(string)
        """

        # TODO: Leads to rewrite if the function is called
        # twice with same 'interface'

        # error_handling.type_verify('Interface', interface, 'Interface', Interface)
        # error_handling.type_verify('Stats', stats, 'list', list)

        # for stat in stats:
        #     if stat not in Experiment.qdisc_stats:
        #         raise ValueError('{} is not a valid Queue property.'.format(stat))

        if interface.get_qdisc() is None:
            raise ValueError('Given interface hasn\'t been assigned any qdisc.')

        self.qdisc_stats.append({
            'ns_id': interface.get_namespace(),
            'int_id': interface.ifb.get_id(),
            'qdisc_handle': interface.get_qdisc().handle,
            'stats': stats
        })

    def get_flows(self):
        """
        Getter for flows in experiment
        """

        return self.flows

    def get_name(self):
        """
        Getter for name of experiment
        """

        return self.name

    def run(self):
        """
        Run the experiment
        """

        # TopologyMap.dump()
        print('Running experiment ' + self.name)
        run_experiment(self) 
