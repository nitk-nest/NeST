# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""API related to interfaces in topology"""

from .address import Address
from .. import engine
from .id_generator import IdGen
from ..topology_map import TopologyMap
from . import traffic_control
from .. import config

# TODO: Improve this module such that the below pylint disables are no
# longer required

#pylint: disable=too-many-instance-attributes
#pylint: disable=protected-access
#pylint: disable=too-few-public-methods

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
        name is only used to display it to the user
        id is the actual backend name
        namespace is of namespace class and not a string
        pair is another object of Interface class to which this is connected

        set_structure tells us if ifb, a default qdisc, netem and HTB are added
        ifb is an object of interface class which tells the ifb associated with this interface

        qdisc_list, class_list, filter_list gives a list of all those as respective classes

        TODO: Add parameter list
        """

        # TODO: name and address should be the only public members
        self._name = interface_name
        self._id = IdGen.get_id(interface_name)

        self._address = None
        self._node = None
        self._pair = None

        self.set_structure = False
        self.ifb = None

        # TODO: These are not rightly updated
        # set_delay and set_bandwidth invoke the
        # engine function directly
        self.qdisc_list = []
        self.class_list = []
        self.filter_list = []

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
                'You should assign the interface to node or router before assigning address to it.')

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

    def set_mode(self, mode):
        """
        Changes the mode of the interface

        Parameters
        ----------
        mode : string
            interface mode to be set
        """
        if mode in ('UP', 'DOWN'):
            if self.node is not None:
                engine.set_interface_mode(
                    self.node.id, self.id, mode.lower())
            else:
                # TODO: Create our own error class
                raise NotImplementedError(
                    'You should assign the interface to node or router before setting it\'s mode')
        else:
            raise ValueError(f'{mode} is not a valid mode (it has to be either "UP" or "DOWN")')

    def get_qdisc(self):
        """
        Note that this is the qdisc set inside
        the IFB.
        """
        if self.ifb is not None:
            for qdisc in self.ifb.qdisc_list:
                if qdisc.parent == '1:1' and qdisc.handle == '11:':
                    return qdisc
        return None

    def add_qdisc(self, qdisc, parent='root', handle='', **kwargs):
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
        self.qdisc_list.append(traffic_control.Qdisc(
            self.node.id, self.id, qdisc, parent, handle, **kwargs))

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
                engine.delete_qdisc(qdisc.namespace_id,
                                    qdisc.dev_id, qdisc.parent, qdisc.handle)
                TopologyMap.delete_qdisc(self.node.id, self.id, handle)
                self.qdisc_list.pop(counter)
                break
            counter += 1

    def add_class(self, qdisc, parent='root', classid='', **kwargs):
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
        self.class_list.append(traffic_control.Class(
            self.node.id, self.id, qdisc, parent, classid, **kwargs))

        return self.class_list[-1]

    #pylint: disable=too-many-arguments
    def add_filter(self, priority, filtertype, flowid, protocol='ip', parent='root',
                   handle='', **kwargs):
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
                self.node.id, self.id, protocol, priority, filtertype,
                flowid, parent, handle, **kwargs))

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
        self.ifb = Interface('ifb-' + dev_name)
        engine.create_ifb(self.ifb.id)

        # Add ifb to namespace
        self.node._add_interface(self.ifb)

        # Set interface up
        self.ifb.set_mode('UP')

        default_route = {
            'default': '1'
        }

        # TODO: find how to set a good bandwidth
        default_bandwidth = {
            'rate': config.get_value('default_bandwidth')
        }

        # TODO: Standardize this; seems like arbitrary handle values
        # were chosen.
        self.ifb.add_qdisc('htb', 'root', '1:', **default_route)
        self.ifb.add_class('htb', '1:', '1:1', **default_bandwidth)
        self.ifb.add_qdisc('pfifo', '1:1', '11:')

        action_redirect = {
            'match': 'u32 0 0',  # from man page examples
            'action': 'mirred',
            'egress': 'redirect',
            'dev': self.ifb.id
        }

        # NOTE: Use Filter API
        engine.add_filter(self.node.id, self.id, 'ip', '1', 'u32', parent='1:', **action_redirect)

    def _set_structure(self):
        """
        Sets a proper structure to the interface by creating HTB class
        with default bandwidth and a netem qdisc as a child.
        (default bandwidth = 1024mbit)
        """
        self.set_structure = True

        default_route = {
            'default': '1'
        }

        self.add_qdisc('htb', 'root', '1:', **default_route)

        # TODO: find how to set a good bandwidth
        default_bandwidth = {
            'rate': config.get_value('default_bandwidth')
        }

        self.add_class('htb', '1:', '1:1', **default_bandwidth)

        self.add_qdisc('netem', '1:1', '11:')

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

        min_bandwidth_parameter = {
            'rate': min_rate
        }

        # TODO: Check the created API
        # TODO: This should be handled by self.change_class
        engine.change_class(self.node.id, self.id, '1:', 'htb', '1:1', **min_bandwidth_parameter)

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

        delay_parameter = {
            'delay': delay
        }

        # TODO: This should be handled by self.change_qdisc
        # It could lead to a potential bug!
        engine.change_qdisc(self.node.id, self.id, 'netem', '1:1', '11:', **delay_parameter)

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

        min_bandwidth_parameter = {
            'rate': bandwidth
        }

        engine.change_class(self.node.id, self.ifb.id,
                            '1:', 'htb', '1:1', **min_bandwidth_parameter)

        self.ifb.delete_qdisc('11:')
        self.ifb.add_qdisc(qdisc, '1:1', '11:', **kwargs)

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
        return f'{classname}({self.name!r})'

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


def connect(ns1, ns2, interface1_name='', interface2_name=''):
    """
    Connects two nodes `ns1` and `ns2`
    """
    # Create 2 interfaces

    if interface1_name == '' and interface2_name == '':
        connections = _number_of_connections(ns1, ns2)
        interface1_name = ns1.name + '-' + ns2.name + '-' + str(connections)
        interface2_name = ns2.name + '-' + ns1.name + '-' + str(connections)

    veth = Veth(interface1_name, interface2_name)
    (int1, int2) = veth._get_interfaces()

    ns1._add_interface(int1)
    ns2._add_interface(int2)

    # Set the proper structure for the veth
    int1._set_structure()
    int2._set_structure()

    int1.set_mode('UP')
    int2.set_mode('UP')

    return (int1, int2)


def _number_of_connections(ns1, ns2):
    """
    Return number of connections between the two namespaces
    """

    connections = 0

    if len(ns1.interfaces) > len(ns2.interfaces):
        ns1, ns2 = ns2, ns1

    for interface in ns1.interfaces:
        if interface.pair.node == ns2:
            connections = connections + 1

    return connections
