# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""API related to interfaces in topology"""

import logging
from nest.input_validator import input_validator
from nest.input_validator.metric import Bandwidth, Delay, Percentage
from nest.topology.veth_end import VethEnd
from nest.topology.ifb import Ifb
from nest.topology import Address
from nest.topology.network import Network
from nest import engine
import nest.config as config

# pylint: disable=cyclic-import
from nest import topology

# Max length of interface when Topology Map is disabled
# i.e. 'assign_random_names' is set to False in config
MAX_CUSTOM_NAME_LEN = 15

logger = logging.getLogger(__name__)

# TODO: Improve this module such that the below pylint disables are no
# longer required

# pylint: disable=too-many-instance-attributes
# pylint: disable=protected-access
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-public-methods


class Interface:
    """
    Abstraction for an network interface.

    Attributes
    ----------
    name : str
        User given name for the interface
    id : str
        This value is used by `engine` to create emulated interface
        entity
    node : Node
        `Node` which contains this `Interface`
    address : str/Address
        IP address assigned to this interface
    """

    @input_validator
    def __init__(self, interface_name: str):
        """
        Constructor of Interface.

        *Note*: The creation of Interface object does not
        create any devices in the interface.
        [See `create_veth_pair` method]

        Parameters
        ----------
        interface_name : str
            Name of the interface
        """

        self._veth_end = VethEnd(interface_name, None)
        self._ifb = None

    @property
    def name(self):
        """Getter for name"""
        return self._veth_end.name

    @property
    def id(self):
        """Getter for id"""
        return self._veth_end.id

    @property
    def pair(self):
        """
        Get other pair for this interface (assuming veth)
        """
        return self._pair

    @pair.setter
    def pair(self, interface):
        """
        Setter for the other end of the interface that it is connected to

        Parameters
        ----------
        interface : Interface
            The interface to which this interface is connected to
        """
        self._pair = interface

    @property
    def node_id(self):
        """
        Getter for the `Node` associated
        with the interface
        """
        return self._veth_end.node_id

    @node_id.setter
    def node_id(self, node_id):
        """
        Setter for the `Node` associated
        with the interface

        Parameters
        ----------
        node : Node
            The node where the interface is to be installed
        """
        self._veth_end.node_id = node_id

    @property
    def ifb_id(self):
        """
        Getter for the id of the ifb of
        the interface
        """
        return self._ifb.id

    @property
    def subnet(self):
        """Getter for the subnet to which the address belongs to"""
        return self._veth_end.address.get_subnet()

    @property
    def address(self):
        """
        Getter for the address associated
        with the interface
        """
        return self._veth_end.address

    @address.setter
    @input_validator
    def address(self, address: Address):
        """
        Assigns IP address to an interface

        Parameters
        ----------
        address : Address or str
            IP address to be assigned to the interface
        """
        self._veth_end.address = address

    def enable_mpls(self):
        """
        Enables mpls input through the interface.
        Requires mpls kernel modules to be loaded.

        Run ``sudo modprobe mpls_iptunnel`` to load mpls modules.
        """
        self._veth_end.enable_mpls()

    def is_mpls_enabled(self):
        """
        Check if the interface has mpls enabled
        """
        return self._veth_end.is_mpls_enabled()

    @property
    def mtu(self):
        """
        Get the maximum transmit unit value for the interface
        """
        return self._veth_end.mtu

    @mtu.setter
    def mtu(self, mtu_value):
        """
        Set the maximum transmit unit value for the interface
        Default is 1500 bytes.
        """
        self._veth_end.mtu = mtu_value

    def get_address(self):
        """
        Getter for the address associated
        with the interface

        *NOTE*: Maintained since mentioned in NeST paper.
        """
        return self._veth_end.address

    @input_validator
    def set_address(self, address: Address):
        """
        Assigns IP address to an interface

        Parameters
        ----------
        address : Address or str
            IP address to be assigned to the interface

        *NOTE*: Maintained since mentioned in NeST paper.
        """
        self._veth_end.address = address

    def disable_ip_dad(self):
        """
        Disables Duplicate addresses Detection (DAD) for an interface.
        """
        self._veth_end.disable_ip_dad()

    def set_mode(self, mode):
        """
        Changes the mode of the interface

        Parameters
        ----------
        mode : string
            interface mode to be set
        """
        self._veth_end.set_mode(mode)

    def get_qdisc(self):
        """
        Note that this is the qdisc set inside
        the IFB.
        """
        if self._ifb is not None:
            for qdisc in self._ifb.qdisc_list:
                if qdisc.parent == "1:1" and qdisc.handle == "11:":
                    return qdisc
        return None

    def _create_and_mirred_to_ifb(self):
        """
        Creates a IFB for the interface so that a Qdisc can be
        installed on it
        Mirrors packets to be sent out of the interface first to
        itself (IFB)
        Assumes the interface has already invoked _set_structure()

        Parameters
        ----------
        """

        ifb_name = "ifb-" + self.name
        self._ifb = Ifb(ifb_name, self.node_id, self.id)

    @input_validator
    def set_bandwidth(self, bandwidth: Bandwidth):
        """
        Sets a minimum bandwidth for the interface
        It is done by adding a HTB qdisc and a rate parameter to the class

        Parameters
        ----------
        bandwidth : Bandwidth
            The minimum rate that has to be set in kbit
        """

        self._veth_end.set_structure()
        if self._ifb is not None:
            # Set the same bandwidth in the IFB too
            self._ifb.set_bandwidth(bandwidth.string_value)

        bandwidth_parameter = {"rate": bandwidth.string_value}

        self._veth_end.change_class("htb", "1:", "1:1", **bandwidth_parameter)

    @input_validator
    def set_delay(self, delay: Delay):
        """
        Adds a delay to the link between two namespaces
        It is done by adding a delay in the interface

        Parameters
        ----------
        delay : Delay
            The delay to be added
        """
        # TODO: Make adding delay possible without bandwidth being set

        self._veth_end.set_structure()

        delay_parameter = {"delay": delay.string_value}

        self._veth_end.change_qdisc("11:", "netem", **delay_parameter)

    @input_validator
    def set_packet_corruption(
        self, corrupt_rate: Percentage, correlation_rate: Percentage = None
    ):
        """
        allows the emulation of random noise introducing an error in a
        random position for a chosen percent of packets.
        It is also possible to add a correlation.

        Parameters
        ----------
        corrupt_rate : str
            rate of the packets to be corrupted
        correlation_rate : str
            correlation between the corrupted packets
        """
        parsed_correlation_rate = (
            correlation_rate.string_value if correlation_rate else ""
        )

        self._veth_end.set_structure()

        corrupt_parameter = {
            "corrupt": corrupt_rate.string_value,
            "": parsed_correlation_rate,
        }

        self._veth_end.change_qdisc("11:", "netem", **corrupt_parameter)

    @input_validator
    def set_packet_loss(
        self, loss_rate: Percentage, correlation_rate: Percentage = None
    ):
        """
        adds an independent loss probability to the packets outgoing from
        the chosen network interface.
        It is also possible to add a correlation

        Parameters
        ----------
        loss_rate : str
            rate of the packets to be lost
        correlation_rate : str
            correlation between the lost packets
        """
        parsed_correlation_rate = (
            correlation_rate.string_value if correlation_rate else ""
        )

        self._veth_end.set_structure()

        loss_parameter = {"loss": loss_rate.string_value, "": parsed_correlation_rate}

        self._veth_end.change_qdisc("11:", "netem", **loss_parameter)

    def set_qdisc(self, qdisc, **kwargs):
        """
        Adds the Queueing algorithm to the interface

        Parameters
        ----------
        qdisc : string
            The Queueing algorithm to be added
        bandwidth :
            Link bandwidth
        """
        # TODO: Check if this is a redundant condition

        self._veth_end.set_structure()

        if self._ifb is None:
            self._create_and_mirred_to_ifb()

        self._ifb.delete_qdisc("11:")
        self._ifb.add_qdisc(qdisc, "1:1", "11:", **kwargs)

    @input_validator
    def set_attributes(
        self, bandwidth: Bandwidth, delay: Delay, qdisc: str = None, **kwargs
    ):
        """
        Add attributes bandwidth, delay and qdisc to interface

        Parameters
        ----------
        bandwidth : str/Bandwidth
            Packet outgoing rate
        delay : str/Delay
            Delay before packet is sent out
        qdisc : string
            The Queueing algorithm to be added to interface
            (Default value = None)
        """

        self.set_bandwidth(bandwidth)
        self.set_delay(delay)

        if qdisc is not None:
            self.set_qdisc(qdisc, **kwargs)

    def enable_offload(self, offload_name):
        """
        API for enabling offloads
        Parameters
        ----------
        offload_name : str
            The type of offload names that need to enable
        """

        self._veth_end.enable_offload(offload_name)

    def disable_offload(self, offload_name):
        """
        API for disabling offloads
        Parameters
        ----------
        offload_name : str
            The type of offload names that need to disable
        """

        self._veth_end.disable_offload(offload_name)

    def __repr__(self):
        classname = self.__class__.__name__
        return f"{classname}({self.name!r})"


def create_veth_pair(interface1_name, interface2_name):
    """
    Handle creation of Veth pairs between
    `interface1_name` and `interface2_name`

    Parameters
    ----------
    interface1_name : str
            Name of one of the interfaces to be connected
    interface2_name : str
            Name of the other interface to be connected
    """

    interface1 = Interface(interface1_name)
    interface2 = Interface(interface2_name)

    interface1.pair = interface2
    interface2.pair = interface1

    # Create the veth
    engine.create_veth(interface1.id, interface2.id)

    return (interface1, interface2)


@input_validator
def connect(
    node1: topology.Node,
    node2: topology.Node,
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
    if network is not None:
        network.add_interface(interface1)
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
