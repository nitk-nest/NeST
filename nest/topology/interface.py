# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""API related to interfaces in topology"""

import logging
from nest import engine
from nest.topology_map import TopologyMap
import nest.global_variables as g_var
import nest.config as config
from .address import Address
from .id_generator import IdGen
from . import traffic_control

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
    name: str
        User given name for the interface
    id: str
        This value is used by `engine` to create emulated interface
        entity
    node: Node
        `Node` which contains this `Interface`
    address: str/Address
        IP address assigned to this interface
    """

    def __init__(self, interface_name):
        """
        Constructor of Interface.

        *Note*: Unlike Node object, the creation of Interface object
        does not actually create an interface in the backend. This has
        to be done seperately by invoking engine.
        [See `Veth` class for an example]

        Parameters
        ----------
        interface_name : str
            Name of the interface
        """

        if config.get_value("assign_random_names") is False:
            if len(interface_name) > MAX_CUSTOM_NAME_LEN:
                raise ValueError(
                    f"Interface name {interface_name} is too long. Interface names "
                    f"should not exceed 15 characters"
                )

        # TODO: name and address should be the only public members
        self._name = interface_name
        self._id = IdGen.get_id(interface_name)

        self._address = None
        self._node = None
        self._pair = None
        # Normally this is the default mtu value.
        self._mtu = 1500

        self.set_structure = False
        self.ifb = None

        # TODO: These are not rightly updated
        # set_delay and set_bandwidth invoke the
        # engine function directly
        self.qdisc_list = []
        self.class_list = []
        self.filter_list = []

        # mpls input
        self._is_mpls_enabled = False

    @property
    def name(self):
        """Getter for name"""
        return self._name

    @property
    def id(self):
        """Getter for id"""
        return self._id

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
    def node(self):
        """
        Getter for the `Node` associated
        with the interface
        """
        return self._node

    @node.setter
    def node(self, node):
        """
        Setter for the `Node` associated
        with the interface

        Parameters
        ----------
        node : Node
            The node where the interface is to be installed
        """
        self._node = node

    @property
    def subnet(self):
        """Getter for the subnet to which the address belongs to"""
        return self.address.get_subnet()

    @property
    def address(self):
        """
        Getter for the address associated
        with the interface
        """
        return self._address

    @address.setter
    def address(self, address):
        """
        Assigns IP address to an interface

        Parameters
        ----------
        address : Address or str
            IP address to be assigned to the interface
        """
        if isinstance(address, str):
            address = Address(address)

        if self.node is not None:
            engine.assign_ip(self.node.id, self.id, address.get_addr())
            self._address = address
        else:
            # TODO: Create our own error class
            raise NotImplementedError(
                "You should assign the interface to node or router before assigning address to it."
            )

        # Global variable to check if address is ipv6 or not for DAD check
        if address.is_ipv6() is True:
            g_var.IS_IPV6 = True

    def enable_mpls(self):
        """
        Enables mpls input through the interface.
        Requires mpls kernel modules to be loaded.

        Run ``sudo modprobe mpls_iptunnel`` to load mpls modules.
        """
        if self.node is None:
            raise NotImplementedError(
                "You should assign the interface to node or router before enabling mpls"
            )
        if self.node.mpls_max_label == 0:
            # property setter.
            # Alters: net.mpls.platform_labels=100000
            self.node.mpls_max_label = 100000

        if self._is_mpls_enabled is False:
            engine.enable_mpls_interface(self.node.id, self.id)
            self._is_mpls_enabled = True
            self.mtu = 1504

    def is_mpls_enabled(self):
        """
        Check if the interface has mpls enabled
        """
        return self._is_mpls_enabled

    @property
    def mtu(self):
        """
        Get the maximum transmit unit value for the interface
        """
        return self._mtu

    @mtu.setter
    def mtu(self, mtu_value):
        """
        Set the maximum transmit unit value for the interface
        Default is 1500 bytes.
        """
        if self._mtu != mtu_value:
            engine.set_mtu_interface(self.node.id, self.id, int(mtu_value))
            self._mtu = mtu_value
            logger.debug("MTU of interface %s set to %s", self.name, str(self.mtu))

    def get_address(self):
        """
        Getter for the address associated
        with the interface

        *NOTE*: Maintained since mentioned in NeST paper.
        """
        return self.address

    def set_address(self, address):
        """
        Assigns IP address to an interface

        Parameters
        ----------
        address : Address or str
            IP address to be assigned to the interface

        *NOTE*: Maintained since mentioned in NeST paper.
        """
        self.address = address

    def disable_ip_dad(self):
        """
        Disables Duplicate addresses Detection (DAD) for an interface.
        """
        engine.disable_dad(self._node.id, self._id)

    def set_mode(self, mode):
        """
        Changes the mode of the interface

        Parameters
        ----------
        mode : string
            interface mode to be set
        """
        if mode in ("UP", "DOWN"):
            if self.node is not None:
                engine.set_interface_mode(self.node.id, self.id, mode.lower())
            else:
                # TODO: Create our own error class
                raise NotImplementedError(
                    "You should assign the interface to node or router before setting it's mode"
                )
        else:
            raise ValueError(
                f'{mode} is not a valid mode (it has to be either "UP" or "DOWN")'
            )

    def get_qdisc(self):
        """
        Note that this is the qdisc set inside
        the IFB.
        """
        if self.ifb is not None:
            for qdisc in self.ifb.qdisc_list:
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
        self.qdisc_list.append(
            traffic_control.Qdisc(
                self.node.id, self.id, qdisc, parent, handle, **kwargs
            )
        )

        # Add qdisc to TopologyMap
        TopologyMap.add_qdisc(self.node.id, self.id, qdisc, handle, parent=parent)

        return self.qdisc_list[-1]

    def delete_qdisc(self, handle):
        """
        Delete qdisc (Queueing Discipline) from this interface

        Parameters
        ----------
        handle : string
            Handle of the qdisc to be deleted
        """
        # TODO: Handle this better by using the destructor in traffic-control
        counter = 0
        for qdisc in self.qdisc_list:
            if qdisc.handle == handle:
                engine.delete_qdisc(
                    qdisc.namespace_id, qdisc.dev_id, qdisc.parent, qdisc.handle
                )
                TopologyMap.delete_qdisc(self.node.id, self.id, handle)
                self.qdisc_list.pop(counter)
                break
            counter += 1

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
        self.class_list.append(
            traffic_control.Class(
                self.node.id, self.id, qdisc, parent, classid, **kwargs
            )
        )

        return self.class_list[-1]

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

        self.filter_list.append(
            traffic_control.Filter(
                self.node.id,
                self.id,
                protocol,
                priority,
                filtertype,
                flowid,
                parent,
                handle,
                **kwargs,
            )
        )

        return self.filter_list[-1]

    def _create_and_mirred_to_ifb(self, dev_name):
        """
        Creates a IFB for the interface so that a Qdisc can be
        installed on it
        Mirrors packets to be sent out of the interface first to
        itself (IFB)
        Assumes the interface has already invoked _set_structure()

        Parameters
        ----------
        dev_name : string
            The interface to which the ifb was added
        """
        ifb_name = "ifb-" + dev_name
        if config.get_value("assign_random_names") is False:
            if len(ifb_name) > MAX_CUSTOM_NAME_LEN:
                raise ValueError(
                    f"Auto-generated IFB interface name {ifb_name} is too long. "
                    f"The length of name should not exceed 15 characters."
                )

        self.ifb = Interface(ifb_name)
        engine.create_ifb(self.ifb.id)

        # Add ifb to namespace
        self.node._add_interface(self.ifb)

        # Set interface up
        self.ifb.set_mode("UP")

        default_route = {"default": "1"}

        # TODO: find how to set a good bandwidth
        default_bandwidth = {"rate": config.get_value("default_bandwidth")}

        # TODO: Standardize this; seems like arbitrary handle values
        # were chosen.
        self.ifb.add_qdisc("htb", "root", "1:", **default_route)
        self.ifb.add_class("htb", "1:", "1:1", **default_bandwidth)
        self.ifb.add_qdisc("pfifo", "1:1", "11:")

        action_redirect = {
            "match": "u32 0 0",  # from man page examples
            "action": "mirred",
            "egress": "redirect",
            "dev": self.ifb.id,
        }

        # NOTE: Use Filter API
        engine.add_filter(
            self.node.id, self.id, "all", "1", "u32", parent="1:", **action_redirect
        )

    def _set_structure(self):
        """
        Sets a proper structure to the interface by creating HTB class
        with default bandwidth and a netem qdisc as a child.
        (default bandwidth = 1024mbit)
        """
        self.set_structure = True

        default_route = {"default": "1"}

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

        if self.set_structure is False:
            self._set_structure()

        min_bandwidth_parameter = {"rate": min_rate}

        # TODO: Check the created API
        # TODO: This should be handled by self.change_class
        engine.change_class(
            self.node.id, self.id, "1:", "htb", "1:1", **min_bandwidth_parameter
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

        # TODO: This should be handled by self.change_qdisc
        # It could lead to a potential bug!
        engine.change_qdisc(
            self.node.id, self.id, "netem", "1:1", "11:", **delay_parameter
        )

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

        engine.change_qdisc(
            self.node.id, self.id, "netem", "1:1", "11:", **corrupt_parameter
        )

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

        engine.change_qdisc(
            self.node.id, self.id, "netem", "1:1", "11:", **loss_parameter
        )

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

        if self.ifb is None:
            self._create_and_mirred_to_ifb(self.name)

        min_bandwidth_parameter = {"rate": bandwidth}

        engine.change_class(
            self.node.id, self.ifb.id, "1:", "htb", "1:1", **min_bandwidth_parameter
        )

        self.ifb.delete_qdisc("11:")
        self.ifb.add_qdisc(qdisc, "1:1", "11:", **kwargs)

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


class Veth:
    """Handle creation of Veth pairs"""

    def __init__(self, interface1_name, interface2_name):
        """
        Constructor to create a veth pair between
        `interface1_name` and `interface2_name`
        """

        self.interface1 = Interface(interface1_name)
        self.interface2 = Interface(interface2_name)

        self.interface1.pair = self.interface2
        self.interface2.pair = self.interface1

        # Create the veth
        engine.create_veth(self.interface1.id, self.interface2.id)

    def _get_interfaces(self):
        """Get tuple of endpoint interfaces"""

        return (self.interface1, self.interface2)


def connect(node1, node2, interface1_name="", interface2_name=""):
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
    veth = Veth(interface1_name, interface2_name)
    (interface1, interface2) = veth._get_interfaces()

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
        if interface.pair.node == node2:
            connections = connections + 1

    return connections
