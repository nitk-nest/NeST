# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""User API to setup and run experiments on a given topology"""

import copy
import logging
from nest.network_utilities import ipv6_dad_check
from ..topology import Address
from .run_exp import run_experiment
from .pack import Pack

logger = logging.getLogger(__name__)

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
class Flow:
    """Defines a flow in the topology"""

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        source_node,
        destination_node,
        destination_address,
        start_time,
        stop_time,
        number_of_streams,
    ):
        """
        'Flow' object in the topology

        Parameters
        ----------
        source_node : Node
            Source node of flow
        destination_node : Node
            Destination node of flow
        destination_address : Address/str
            Destination address of flow
        start_time : int
            Time to start flow (in seconds)
        stop_time : int
            Time to stop flow (in seconds)
        number_of_streams : int
            Number of streams in the flow
        """
        self.source_node = source_node
        self.destination_node = destination_node
        self.destination_address = destination_address
        self.start_time = start_time
        self.stop_time = stop_time
        self.number_of_streams = number_of_streams

        self._options = {"protocol": "TCP", "cong_algo": "cubic"}

    @property
    def destination_address(self):
        """Getter for destination address"""
        return self._destination_address

    @destination_address.setter
    def destination_address(self, destination_address):
        """Setter for destination address"""
        if isinstance(destination_address, str):
            destination_address = Address(destination_address)
        self._destination_address = destination_address

    def _get_props(self):
        """
        Get flow properties.

        NOTE: To be used internally
        """

        return [
            self.source_node.id,
            self.destination_node.id,
            self.destination_address.get_addr(with_subnet=False),
            self.start_time,
            self.stop_time,
            self.number_of_streams,
            self._options,
        ]

    def __repr__(self):
        classname = self.__class__.__name__
        return (
            f"{classname}({self.source_node!r}, {self.destination_node!r},"
            f" {self.destination_address!r}), {self.start_time!r}, {self.stop_time!r}"
            f" {self.number_of_streams!r})"
        )


class Experiment:
    """Handles experiment to be run on topology"""

    def __init__(self, name):
        """
        Create experiment

        Parameters
        ----------
        name : str
            Name of experiment
        """
        self.name = name
        self.flows = []
        self.node_stats = []
        self.qdisc_stats = []

    def add_flow(self, flow):
        """
        Add flow to experiment
        By default, the flow is assumed to be
        TCP with cubic congestion algorithm

        Parameters
        ----------
        flow : Flow
            Add flow to experiment
        """
        self.flows.append(copy.deepcopy(flow))

    def add_tcp_flow(self, flow, congestion_algorithm="cubic"):
        """
        Add TCP flow to experiment

        Parameters
        ----------
        flow : Flow
            Flow to be added to experiment
        congestion_algorithm : str
            TCP congestion algorithm (Default value = 'cubic')
        """

        # TODO: Verify congestion algorithm

        options = {"protocol": "TCP", "cong_algo": congestion_algorithm}

        flow._options = options  # pylint: disable=protected-access
        self.add_flow(flow)

    def add_udp_flow(self, flow, target_bandwidth="1mbit"):
        """
        Add UDP flow to experiment

        Parameters
        ----------
        flow : Flow
            Flow to be added to experiment
        target_bandwidth :
            UDP bandwidth (in Mbits) (Default value = '1mbit')
            This bandwidth limit is for each UDP stream in the flow
        """
        if len(target_bandwidth) < 4 or target_bandwidth[-4:] != "mbit":
            raise Exception(
                "Invalid bandwidth unit given to target_bandwidth parameter. "
                "Expecting mbit."
            )

        options = {"protocol": "UDP", "target_bw": target_bandwidth}

        flow._options = options  # pylint: disable=protected-access
        self.add_flow(flow)

    def require_qdisc_stats(self, interface, stats=""):
        """
        Stats to be obtained from qdisc in interface

        Parameters
        ----------
        interface : Interface
            Interface containing the qdisc
        stats : list(str)
            Stats required (Default value = '') [NOT SUPPORTED]
        """
        # TODO: Leads to rewrite if the function is called
        # twice with same 'interface'

        # for stat in stats:
        #     if stat not in Experiment.qdisc_stats:
        #         raise ValueError('{} is not a valid Queue property.'.format(stat))

        if interface.get_qdisc() is None:
            raise ValueError("Given interface hasn't been assigned any qdisc.")

        self.qdisc_stats.append(
            {
                "ns_id": interface.node.id,
                "int_id": interface.ifb.id,
                "qdisc": interface.get_qdisc().qdisc,
                "stats": stats,
            }
        )

    @ipv6_dad_check
    def run(self):
        """Run the experiment"""
        print()
        logger.info("Running experiment %s ", self.name)
        Pack.init(self.name)
        run_experiment(self)

    def __repr__(self):
        classname = self.__class__.__name__
        return f"{classname}({self.name!r})"
