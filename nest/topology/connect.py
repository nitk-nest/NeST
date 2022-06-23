# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""
API implementation of `connect`.
"""

from nest import config
from nest.input_validator import input_validator
from nest.topology import Switch
from nest.topology.interface import create_veth_pair
from nest.topology.network import Network
from nest.topology import Node
from nest.topology_map import TopologyMap

# Max length of interface when Topology Map is disabled
# i.e. 'assign_random_names' is set to False in config
MAX_CUSTOM_NAME_LEN = 15


@input_validator
def connect(
    node1: Node,
    node2: Node,
    interface1_name: str = "",
    interface2_name: str = "",
    network: Network = None,
):
    """
    Connects two nodes `node1` and `node2`.
    Creates two paired Virtual Ethernet interfaces (veth) and returns
    them as a 2-element tuple.
    The first interface belongs to `node1`, and the second interface
    belongs to `node2`.

    Parameters
    ----------
    node1 : Node
        First veth interface added in this node
    node2 : Node
        Second veth interface added in this node
    interface1_name : str
        Name of first veth interface
    interface2_name : str
        Name of second veth interface
    network : Network
        Object of the Network to add interfaces

    Returns
    -------
    (interface1, interface2)
        2 tuple of created (paired) veth interfaces. `interface1` is in
        `n1` and `interface2` is in `n2`.
    """
    # Number of connections between `node1` and `node2`, set to `None`
    # initially since it hasn't been computed yet
    connections = None

    # Check interface names
    if interface1_name == "":
        connections = _number_of_connections(node1, node2)
        interface1_name = _autogenerate_interface_name(node1, node2, connections)

    if interface2_name == "":
        if connections is None:
            connections = _number_of_connections(node1, node2)
        # pylint: disable=arguments-out-of-order
        interface2_name = _autogenerate_interface_name(node2, node1, connections)

    # Create 2 interfaces
    (interface1, interface2) = create_veth_pair(interface1_name, interface2_name)

    # pylint: disable=protected-access
    node1._add_interface(interface1)
    node2._add_interface(interface2)

    interface1.set_mode("UP")
    interface2.set_mode("UP")

    # Disabling Duplicate Address Detection(DAD) at the interfaces
    if config.get_value("disable_dad") is True:
        interface1.disable_ip_dad()
        interface2.disable_ip_dad()

    # The network parameter takes precedence over "global" network level
    if network is None:
        network = Network.current_network

    # Add the interfaces to the network if mentioned
    # For switch, add the switch interface to the network(not veth end) and decrement the
    # count of orphan interface to remove veth end from the list of orphan interfaces
    if network is not None:
        if isinstance(node1, Switch):
            network.add_interface(node1)
            TopologyMap.decrement_orphan_interfaces()
        else:
            network.add_interface(interface1)

        if isinstance(node2, Switch):
            network.add_interface(node2)
            TopologyMap.decrement_orphan_interfaces()
        else:
            network.add_interface(interface2)

    return (interface1, interface2)


def _autogenerate_interface_name(node1, node2, connections):
    """
    Auto-generate interface names based on respective node names
    and number of connections
    """
    interface_name = node1.name + "-" + node2.name + "-" + str(connections)

    if config.get_value("assign_random_names") is False:
        if len(interface_name) > MAX_CUSTOM_NAME_LEN:
            raise ValueError(
                f"Auto-generated device name {interface_name} is too long. "
                f"The length of name should not exceed 15 characters."
            )

    return interface_name


def _number_of_connections(node1, node2):
    """
    Return number of connections between the two nodes
    """
    connections = 0

    if len(node1.interfaces) > len(node2.interfaces):
        node1, node2 = node2, node1

    for interface in node1.interfaces:
        if interface.pair.node_id == node2.id:
            connections = connections + 1

    return connections
