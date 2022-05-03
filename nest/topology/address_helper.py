# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""API related to Address Helper"""

import logging
from nest.input_validator.input_validator import input_validator
from nest.topology.network import Network
from nest.topology_map import TopologyMap
from .address import Subnet

# pylint: disable=too-few-public-methods

logger = logging.getLogger(__name__)


class AddressHelper:
    """
    Abstraction for automatic address assignment to interfaces of the network.
    """

    @staticmethod
    @input_validator
    def assign_addresses(network: Network = None):
        """
        Assignment of addresses to the interfaces.

        Parameters
        ----------
        network : Network
            Assigning the addresses to each interfaces of all network.
            It will assign addresses to specific network if network object is mentioned.
        """
        if network is None:

            networks = TopologyMap.get_networks()
            for net in networks:
                AddressHelper.__assign_addresses_to_network(net)

            # Warning for the assignment of the addresses to the interfaces,
            # which do not belong to any network
            if TopologyMap.orphan_interfaces != 0:
                logger.warning(
                    "Interfaces not part of some network. The addresses to these orphaned "
                    "interfaces should be manually added.",
                )
        else:
            AddressHelper.__assign_addresses_to_network(network)

    @staticmethod
    def __assign_addresses_to_network(network: Network):
        """
        Assignment of addresses to all interfaces of specific network.

        Parameters
        ----------
        network : Network
            Assigning the addresses to each interfaces of the given network object.
        """
        _interfaces = []
        _interfaces = network.interfaces

        _net_address = Subnet(network.net_address)

        for inter in _interfaces:
            inter.set_address(_net_address.get_next_addr())
