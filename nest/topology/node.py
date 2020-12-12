# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""API related to node creation in topology"""

import logging

from .address import Address
from .. import engine
from .id_generator import IdGen
from ..topology_map import TopologyMap

logger = logging.getLogger(__name__)


class Node:
    """
    Abstraction for a network namespace.

    Attributes
    ----------
    name: str
        User given name for the node.
    """

    def __init__(self, name):
        """
        Create a node with given `name`.

        An unique `id` is assigned to this node which is used by
        `engine` module to create the network namespace.
        This ensures that there is no naming conflict between any two
        nodes.

        Parameters
        ----------
        name: str
            The name of the node to be created
        """
        if name == '':
            raise ValueError('Node name can\'t be an empty string')

        self._name = name
        self._id = IdGen.get_id(name)
        self._interfaces = []

        engine.create_ns(self.id)
        TopologyMap.add_namespace(self.id, self.name)
        TopologyMap.add_host(self)

    def add_route(self, dest_addr, via_interface, next_hop_addr=''):
        """
        Add a route to the routing table of `Node`.

        Parameters
        ----------
        dest_addr: Address/str
            Destination IP address of node to route to. 'DEFAULT' is
            for all addresses
        via_interface: Interface
            `Interface` in `Node` to route via
        next_hop_addr: Address/str, optional
            IP address of next hop Node (or router), by default ''
        """
        if isinstance(dest_addr, str):
            dest_addr = Address(dest_addr)

        if next_hop_addr != '':
            if isinstance(next_hop_addr, str):
                next_hop_addr = Address(next_hop_addr)
        else:
            # Assuming veth pair
            next_hop_addr = via_interface.pair.address

        dest_addr_str = ''
        if dest_addr.is_subnet():
            dest_addr_str = dest_addr.get_addr()
        else:
            dest_addr_str = dest_addr.get_addr(with_subnet=False)

        engine.add_route(
            self.id, dest_addr_str, next_hop_addr.get_addr(with_subnet=False),
            via_interface.id)

    def _add_interface(self, interface):
        """
        Add `interface` to `Node`

        Parameters
        ----------
        interface: Interface
            `Interface` to be added to `Node`
        """
        self._interfaces.append(interface)
        interface.node = self
        engine.add_int_to_ns(self.id, interface.id)
        TopologyMap.add_interface(
            self.id, interface.id, interface.name)

    def configure_tcp_param(self, param, value):
        """
        Configure TCP parameters of `Node` available at
        /proc/sys/net/ipv4/tcp_*.

        Example: 'window_scaling', 'wmem', 'ecn', etc.

        Parameters
        ----------
        param: str
            TCP parameter to be configured
        value: str
            New value of TCP parameter `param`

        Returns
        -------
        str
            If TCP Parameter `param` is valid, then new `value` is set
            for this `param`.
        """
        engine.configure_kernel_param(self.id, 'net.ipv4.tcp_', param, value)

    def configure_udp_param(self, param, value):
        """
        Configure UDP parameters of `Node` available at
        /proc/sys/net/ipv4/udp_*.

        Example: 'early_demux', 'l3mdev_accept', 'rmem_min', 'wmem_min'

        Parameters
        ----------
        param: str
            TCP parameter to be configured
        value: str
            New value of TCP parameter `param`

        Returns
        -------
        str
            If TCP Parameter `param` is valid, then new `value` is set
            for this `param`.
        """
        engine.configure_kernel_param(self.id, 'net.ipv4.udp_', param, value)

    def read_tcp_param(self, param):
        """
        Read TCP parameters of `Node` available at
        `/proc/sys/net/ipv4/tcp_*`.

        Example: 'window_scaling', 'wmem', 'ecn', etc.

        Parameters
        ----------
        param: str
            TCP parameter to be read

        Returns
        -------
        str
            If TCP Parameter `param` is valid, then corresponding value
            is returned.

        read tcp_parameters available at /proc/sys/net/ipv4/tcp_*
        Example: window_scaling, wmem, ecn, etc.
        """
        return engine.read_kernel_param(self.id, 'net.ipv4.tcp_', param)

    def read_udp_param(self, param):
        """
        Read UDP parameters of `Node`available at
        `/proc/sys/net/ipv4/udp_*`.

        Example: 'early_demux', 'l3mdev_accept', 'rmem_min', 'wmem_min'

        Parameters
        ----------
        param: str
            UDP parameter to be read

        Returns
        -------
        str
            If UDP Parameter `param` is valid, then corresponding value
            is returned.
        """
        return engine.read_kernel_param(self.id, 'net.ipv4.udp_', param)

    def ping(self, destination_address, verbose=True):
        """
        Ping from current `Node` to destination address
        if there is a route.

        Parameters
        ----------
        destination_address: Address/str
            IP address to ping to
        verbose: bool
            If `True`, print extensive ping success/failure details

        Returns
        -------
        bool
            `True` if `Node` can successfully ping `destination_address`.
            Else `False`.
        """
        if isinstance(destination_address, str):
            destination_address = Address(destination_address)

        status = engine.ping(
            self.id, destination_address.get_addr(with_subnet=False))
        if verbose:
            if status:
                print(f'SUCCESS: ping from {self.name} to '
                        f'{destination_address.get_addr(with_subnet=False)}')
            else:
                print(f'FAILURE: ping from {self.name} to '
                        f'{destination_address.get_addr(with_subnet=False)}')
        return status

    def enable_ip_forwarding(self):
        """
        Enable IP forwarding in `Node`.

        After this method runs, the `Node` can be used as a router.
        """
        engine.en_ip_forwarding(self.id)
        TopologyMap.add_router(self)

    @property
    def id(self):
        """
        str: Value used by `engine` to create the emulated `Node` entity
        """
        return self._id

    @property
    def interfaces(self):
        """list(Interface): List of interfaces in this node"""
        return self._interfaces

    @property
    def name(self):
        """str: User given name for `Node`"""
        return self._name

    def __repr__(self):
        classname = self.__class__.__name__
        return f'{classname}({self.name!r})'
