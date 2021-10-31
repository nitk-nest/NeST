# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""API related to interfaces in topology"""

import logging
from nest.topology.veth_end import VethEnd
from nest.topology.ifb import Ifb
from nest import engine
import nest.config as config

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

    def __init__(self, interface_name):
        """
        Constructor of Interface.

        *Note*: Unlike Node object, the creation of Interface object
        does not actually create an interface in the backend. This has
        to be done seperately by invoking engine.
        [See `create_veth_pair` method]

        Parameters
        ----------
        interface_name : str
            Name of the interface
        """

        # TODO: name and address should be the only public members
        self._veth_end = VethEnd(interface_name, None, None)
        self._current_structure = {"bandwidth": False, "delay": False, "qdisc": False}
        self._ifb = None
        self.set_structure = False

    def enable_offload(self, offload_name):
        """
        API for enabling offloads
        Parameters
        ----------
        offload_name : str
            The type of offload names that need to enable
        """
        if not isinstance(offload_name, list):
            offload_name = [offload_name]
        valid_offloads(offload_name)
        namespace_id = self.node.id
        interface_id = self.id
        for offload_type in offload_name:
            if engine.ethtool.enable_offloads(namespace_id, interface_id, offload_type):
                logger.debug(
                    "%s is enabled on interface %s of %s",
                    offload_type,
                    self.name,
                    self.node.name,
                )
            else:
                logger.error(
                    "%s is not enabled on interface %s of %s",
                    offload_type,
                    self.name,
                    self.node.name,
                )

    def disable_offload(self, offload_name):
        """
        API for disabling offloads
        Parameters
        ----------
        offload_name : str
            The type of offload names that need to disable
        """
        if not isinstance(offload_name, list):
            offload_name = [offload_name]
        valid_offloads(offload_name)
        namespace_id = self.node.id
        interface_id = self.id
        for offload_type in offload_name:
            if engine.ethtool.disable_offloads(
                namespace_id, interface_id, offload_type
            ):
                logger.debug(
                    "%s is disabled on interface %s of %s",
                    offload_type,
                    self.name,
                    self.node.name,
                )
            else:
                logger.error(
                    "%s is not disabled on interface %s of %s",
                    offload_type,
                    self.name,
                    self.node.name,
                )

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
        return self._veth_end.pair

    @pair.setter
    def pair(self, interface):
        """
        Setter for the other end of the interface that it is connected to

        Parameters
        ----------
        interface : Interface
            The interface to which this interface is connected to
        """
        self._veth_end.pair = interface

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
    def address(self, address):
        """
        Assigns IP address to an interface

        Parameters
        ----------
        address : Address or str
            IP address to be assigned to the interface
        """
        self._veth_end.address = address

    @property
    def ifb(self):
        """
        Getter for the ifb attached to this interface
        """
        return self._ifb

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

    def set_address(self, address):
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

    def add_qdisc(self, qdisc, parent="root", handle="", **kwargs):
        """
        Add a qdisc (Queueing Discipline) to this interface

        Parameters
        ----------
        qdisc : string
            The qdisc which needs to be added to the interface
        dev : Interface class
            The interface to which the qdisc is to be added
        parent : string
            id of the parent class in major:minor form(optional) (Default value = 'root')
        handle : string
            id of the filter (Default value = '')
        """
        self._veth_end.add_qdisc(qdisc, parent, handle, **kwargs)

    def delete_qdisc(self, handle):
        """
        Delete qdisc (Queueing Discipline) from this interface

        Parameters
        ----------
        handle : string
            Handle of the qdisc to be deleted
        """
        self._veth_end.delete_qdisc(handle)

    def add_class(self, qdisc, parent="root", classid="", **kwargs):
        """
        Create an object that represents a class

        Parameters
        ----------
        qdisc : string
            The qdisc which needs to be added to the interface
        parent : string
            id of the parent class in major:minor form(optional) (Default value = 'root')
        classid : string
            id of the class (Default value = '')
        """
        self._veth_end.add_class(qdisc, parent, classid, **kwargs)

    # pylint: disable=too-many-arguments
    def add_filter(
        self,
        priority,
        filtertype,
        flowid,
        protocol="ip",
        parent="root",
        handle="",
        **kwargs,
    ):
        """
        Design a Filter to assign to a Class or Qdisc

        Parameters
        ----------
        protocol : string
            protocol used (Default value = 'ip')
        priority : int
            priority of the filter
        filtertype : string
            one of the available filters
        flowid : Class
            classid of the class where the traffic is enqueued
            if the traffic passes the filter
        parent : string
            id of the parent class in major:minor form(optional) (Default value = 'root')
        handle : string
            id of the filter (Default value = '')
        filter : dictionary
            filter parameters
        """
        # TODO: Verify type of parameters
        # TODO: Reduce arguments to the engine functions by finding parent and handle automatically

        self._veth_end.add_filter(
            priority, filtertype, flowid, protocol, parent, handle, **kwargs
        )

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

    def _set_structure(self):
        """
        Sets a proper structure to the interface by creating HTB class
        with default bandwidth and a netem qdisc as a child.
        (default bandwidth = 1024mbit)
        """
        self.set_structure = True

        default_route = {"default": "1"}

        # HTB is added since netem is a classless qdisc. So, htb class,
        # With netem as child is added
        self.add_qdisc("htb", "root", "1:", **default_route)

        # TODO: find how to set a good bandwidth
        default_bandwidth = {"rate": config.get_value("default_bandwidth")}

        self.add_class("htb", "1:", "1:1", **default_bandwidth)

        self.add_qdisc("netem", "1:1", "11:")

    def set_bandwidth(self, min_rate):
        """
        Sets a minimum bandwidth for the interface
        It is done by adding a HTB qdisc and a rate parameter to the class

        Parameters
        ----------
        min_rate : string
            The minimum rate that has to be set in kbit
        """
        # TODO: Check if there exists a delay and if exists, make sure it is handled in the right
        # way
        # TODO: Check if this is a redundant condition
        # TODO: Let user set the unit

        self._set_structure()
        self._create_and_mirred_to_ifb()
        # Set the same bandwidth in the IFB too
        self._ifb.set_bandwidth(min_rate)

        self._current_structure["bandwitdh"] = True

        min_bandwidth_parameter = {"rate": min_rate}

        # TODO: Check the created API
        # TODO: This should be handled by self.change_class
        engine.change_class(
            self.node_id, self.id, "1:", "htb", "1:1", **min_bandwidth_parameter
        )

    def set_delay(self, delay):
        """
        Adds a delay to the link between two namespaces
        It is done by adding a delay in the interface

        Parameters
        ----------
        delay : str
            The delay to be added
        """
        # TODO: It is not intuitive to add delay to an interface
        # TODO: Make adding delay possible without bandwidth being set
        # TODO: Check if this is a redundant condition
        # TODO: Let user set the unit

        if self.set_structure is False:
            self._set_structure()

        delay_parameter = {"delay": delay}

        self._veth_end.change_qdisc("11:", "netem", **delay_parameter)

    def set_packet_corruption(self, corrupt_rate, correlation_rate=""):
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
        if self.set_structure is False:
            self._set_structure()

        corrupt_parameter = {"corrupt": corrupt_rate, "": correlation_rate}

        self._veth_end.change_qdisc("11:", "netem", **corrupt_parameter)

    def set_packet_loss(self, loss_rate, correlation_rate=""):
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

        if self.set_structure is False:
            self._set_structure()

        loss_parameter = {"loss": loss_rate, "": correlation_rate}

        self._veth_end.change_qdisc("11:", "netem", **loss_parameter)

    def set_qdisc(self, qdisc, bandwidth, **kwargs):
        """
        Adds the Queueing algorithm to the interface

        Parameters
        ----------
        qdisc : string
            The Queueing algorithm to be added
        bandwidth :
            Link bandwidth
        """
        # TODO: Don't use this API directly. If it used,
        # then the bandwidth should be same as link bandwidth
        # (A temporary bug fix is causing this issue. Look for
        # a permanent solution)
        # TODO: Check if this is a redundant condition

        if self.set_structure is False:
            self._set_structure()

        if self._ifb is None:
            self._create_and_mirred_to_ifb()

        min_bandwidth_parameter = {"rate": bandwidth}

        self._ifb.change_class("htb", "1:", "1:1", **min_bandwidth_parameter)

        self._ifb.delete_qdisc("11:")
        self._ifb.add_qdisc(qdisc, "1:1", "11:", **kwargs)

    def set_attributes(self, bandwidth, delay, qdisc=None, **kwargs):
        """
        Add attributes bandwidth, delay and qdisc to interface

        Parameters
        ----------
        bandwidth :
            Packet outgoing rate
        delay : string
            Delay before packet is sent out
        qdisc : string
            The Queueing algorithm to be added to interface
            (Default value = None)
        """

        self.set_bandwidth(bandwidth)
        self.set_delay(delay)

        if qdisc is not None:
            self.set_qdisc(qdisc, bandwidth, **kwargs)

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


def connect(node1, node2, interface1_name="", interface2_name="", network=None):
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

    # Set the proper structure for the veth
    interface1._set_structure()
    interface2._set_structure()

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
                f"Auto-generated veth interface name {interface_name} is too long. "
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


def valid_offloads(offload_name):
    """
    Check valid offloads

    Parameters
    -----------
    offload_name : str
        The offload name
    """
    offloads_list = ["tso", "gso", "gro"]
    for offload_type in offload_name:
        if not offload_type in offloads_list:
            logger.error("Invalid offload")
            raise ValueError(f"{offload_type} is not a valid offload")
