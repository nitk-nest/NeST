# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""API related to Network"""

import logging
from nest.topology_map import TopologyMap

logger = logging.getLogger(__name__)


class Network:
    """
    Abstraction for the network of interfaces.

    Attributes
    ----------
    address: str
        IP address of the network

    """

    current_network = None

    def __init__(self, network_address):
        """
        Constructor of Network.

        Parameters
        ----------
        network_address : str
            IP address of the network

        """

        self.net_address = network_address
        self.interface = []

        # Adding each network's object reference to the static list of networks in topology_map.
        TopologyMap.add_network(self)

    def __enter__(self):
        """
        Enter the context of this `Network`.

        """
        # Storing the currently executed network object to the static network variable.
        Network.current_network = self

    def __exit__(self, *args):
        """
        Exit the context of this `Network`.
        """
        Network.current_network = None

    # TODO: Handle the get interface request using the interface list

    def add_interface(self, _interface=None):
        """
        Adding interface to the network.

        Parameters
        ----------
        _interface : interface
            The interface which needs to be added to the Network.
        """
        self.interface.append(_interface)
        TopologyMap.decrement_orphan_interfaces()
