# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""API related to node creation in topology"""

import logging

# pylint: disable=unused-import
# pylint: disable=cyclic-import
from nest import topology
from nest import engine
from nest.topology_map import TopologyMap
import nest.config as config
from nest.network_utilities import ipv6_dad_check
import nest.global_variables as g_var
from nest.input_validator import input_validator
from .address import Address
from .id_generator import IdGen

logger = logging.getLogger(__name__)


class Node:
    """
    Abstraction for a network namespace.

    Attributes
    ----------
    name: str
        User given name for the node.
    """

    @input_validator
    def __init__(self, name: str):
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
        if name == "":
            raise ValueError("Node name can't be an empty string")
        if config.get_value("assign_random_names") is False and len(name) > 3:
            # We chose 3 because: 'ifb-ns1-ns2-20' is a potential IFB interface name
            # and it's already 14 character long. Note that here node names
            # are 'ns1' and 'ns2'. The `ip` utility won't accept interface names
            # longer than 15 characters
            logger.warning(
                "%s is longer than 3 characters. It's safer to use "
                "node names with atmost 3 characters with the current config.",
                name,
            )

        self._name = name
        self._id = IdGen.get_id(name)
        self._interfaces = []
        # Global variable disables when any new node is created
        # to ensure DAD check (if applicable)
        g_var.IS_DAD_CHECKED = False

        engine.create_ns(self.id)
        engine.set_interface_mode(self.id, "lo", "up")
        TopologyMap.add_namespace(self.id, self.name)
        TopologyMap.add_host(self)

    def __enter__(self):
        """
        Enter the context of this `Node`.
        For eg., all commands in this context will only be able to see
        interfaces inside this `Node`
        """
        # Go to network namespace corresponding to `Node`
        engine.set_ns(self.id)

    def __exit__(self, *args):
        """
        Exit the context of this `Node`
        """
        # Switch back to default network namespace
        engine.set_ns(None)

    @input_validator
    def add_route(
        self,
        dest_addr: Address,
        via_interface: "topology.Interface",
        next_hop_addr: Address = None,
    ):
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
        if next_hop_addr is None:
            next_hop_addr = via_interface.pair.address

        dest_addr_str = ""
        if dest_addr.is_subnet():
            dest_addr_str = dest_addr.get_addr()
        else:
            dest_addr_str = dest_addr.get_addr(with_subnet=False)

        engine.add_route(
            self.id,
            dest_addr_str,
            next_hop_addr.get_addr(with_subnet=False),
            via_interface.id,
        )

    def get_interface(self, node, connection_number=1):
        """
        Get the interface in `self` connected to `node`.
        By default, this returns a veth interface.

        `connection_number` is an optional argument used when there
        multiple connections between `self` and `node`.

        Parameters
        ----------
        node: Node
            The other end point of the `veth` interface
        connection_number: int
            If there are multiple connections, then this argument
            uniquely identifies the connection

        Returns
        -------
        Interface
            Return the interface between `self` and `node`. Use
            `connection_number` to uniquly identify an interface if
            there are multiple connections.
            If no interface is found, then return None.
        """
        if connection_number <= 0:
            raise ValueError("connection_number should be greater than 0")

        for interface in self.interfaces:
            if hasattr(interface.pair, "node"):  # True if interface is a `veth`
                pair_node = interface.pair.node
                if node == pair_node:
                    connection_number -= 1

                if connection_number == 0:
                    return interface

        return None

    @input_validator
    def add_route_mpls_push(
        self, dest_addr: Address, next_hop_addr: Address, label: int
    ):
        """
        Add a route to the routing table of `Node`.

        Parameters
        ----------
        dest_addr: Address/str
            Destination ip address of node to route to. 'DEFAULT' is
            for all addresses
        next_hop_addr: Address/str, optional
            IP address of next hop Node (or router), by default ''
        label: the MPLS label pushed onto the packet
        """
        engine.add_mpls_route_push(
            self.id,
            dest_addr.get_addr(),
            next_hop_addr.get_addr(with_subnet=False),
            label,
        )

    @input_validator
    def add_route_mpls_switch(
        self, incoming_label: int, next_hop_addr: Address, outgoing_label: int
    ):
        """

        Parameters
        ----------
        incoming_label: The label that the packet carries when entering the interface
        next_hop_addr: IP address of the next hop
        outgoing_label: The label that is pushed onto the packet

        """
        engine.add_mpls_route_switch(
            self.id,
            incoming_label,
            next_hop_addr.get_addr(with_subnet=False),
            outgoing_label,
        )

    @input_validator
    def add_route_mpls_pop(self, incoming_label: int, next_hop_addr: Address):
        """

        Parameters
        ----------
        incoming_label: THe label that the packet carries when entering the interface
        next_hop_addr: IP address of the next hop

        """
        engine.add_mpls_route_pop(
            self.id, incoming_label, next_hop_addr.get_addr(with_subnet=False)
        )

    def _add_interface(self, interface):
        """
        Add `interface` to `Node`

        Parameters
        ----------
        interface: Interface
            `Interface` to be added to `Node`
        """
        self._interfaces.append(interface)
        interface.node_id = self.id
        engine.add_int_to_ns(self.id, interface.id)

    def configure_tcp_param(self, param, value):
        """
        Configure TCP parameters of `Node` available at
        /proc/sys/net/ipv4/tcp_*.

        Example: 'window_scaling', 'wmem', 'ecn', etc.

        If TCP Parameter `param` is valid, then new `value` is set
        for this `param`.

        Parameters
        ----------
        param: str
            TCP parameter to be configured
        value: str
            New value of TCP parameter `param`
        """
        engine.configure_kernel_param(self.id, "net.ipv4.tcp_", param, value)

    def configure_udp_param(self, param, value):
        """
        Configure UDP parameters of `Node` available at
        /proc/sys/net/ipv4/udp_*.

        Example: 'early_demux', 'l3mdev_accept', 'rmem_min', 'wmem_min'

        If UDP Parameter `param` is valid, then new `value` is set
        for this `param`.

        Parameters
        ----------
        param: str
            TCP parameter to be configured
        value: str
            New value of TCP parameter `param`
        """
        engine.configure_kernel_param(self.id, "net.ipv4.udp_", param, value)

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
        """
        return engine.read_kernel_param(self.id, "net.ipv4.tcp_", param)

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
        return engine.read_kernel_param(self.id, "net.ipv4.udp_", param)

    @ipv6_dad_check
    @input_validator
    def ping(
        self, destination_address: Address, packets: int = 5, verbose: bool = True
    ):
        """
        Ping from current `Node` to destination address
        if there is a route.

        Parameters
        ----------
        destination_address: Address/str
            IP address to ping to
        packets: int
            Number of ping packets sent
        verbose: bool
            If `True`, output ping packet details

        Returns
        -------
        bool
            `True` if `Node` can successfully ping `destination_address`.
            Else `False`.
        """
        if isinstance(destination_address, str):
            destination_address = Address(destination_address)

        if verbose:
            print()
            print(
                f"=== PING from {self.name} to "
                f"{destination_address.get_addr(with_subnet=False)} ==="
            )
            print()

        status = engine.ping(
            self.id,
            destination_address.get_addr(with_subnet=False),
            packets,
            destination_address.is_ipv6(),
            live_output=verbose,
        )

        return status

    def enable_ip_forwarding(self, ipv4=True, ipv6=True):
        """
        Enable IP forwarding in `Node`.

        After this method runs, the `Node` can be used as a router.
        """
        if not ipv4 and not ipv6:
            raise Exception(
                "IP Forwarding cannot be false for both IPv4 and IPv6 addresses"
            )

        engine.en_ip_forwarding(self.id, ipv4, ipv6)
        TopologyMap.add_router(self)

    def disable_ip_dad(self):
        """
        Disables Duplicate addresses Detection (DAD) for all interfaces of `Node`.
        """
        for i in range(len(self._interfaces)):
            interface_name = self._interfaces[i]
            interface_name.disable_ip_dad()

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
        return f"{classname}({self.name!r})"
