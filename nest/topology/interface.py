# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# API related to interfaces in topology
from .address import Address
from .. import engine
from .. import error_handling
from .id_generator import ID_GEN
from ..topology_map import TopologyMap
from . import traffic_control
from .node import Node, Router


class Interface:

    def __init__(self, interface_name, pair=''):
        """
        name is only used to display it to the user
        id is the actual backend name
        namespace is of namespace class and not a string
        pair is another object of Interface class to which this is connected

        set_structure tells us if ifb, a default qdisc, netem and htb are added
        ifb is an object of interface class which tells the ifb associated with this interface

        qdisc_list, class_list, filter_list gives a list of all those as respective classes

        TODO: Add parameter list
        """

        error_handling.type_verify(
            'interface_name', interface_name, 'string', str)
        error_handling.type_verify('pair', pair, 'string', str)

        self.name = interface_name
        self.id = ID_GEN.get_id(interface_name)
        self.namespace = None
        self.pair = None
        self.address = None

        self.set_structure = False
        self.ifb = None

        # TODO: These are not rightly updated
        # set_delay and set_bandwidth invoke the
        # engine function directly
        self.qdisc_list = []
        self.class_list = []
        self.filter_list = []

    def _set_pair(self, interface):
        """
        Setter for the other end of the interface that it is connected to

        :param interface_name: The interface to which this interface is connected to
        :type interface_name: Interface
        """

        self.pair = interface

    def get_pair(self):
        """
        Getter for the interface to which this interface is connected to
        
        :return: Interface to which this interface is connected to
        :r_type: Interface            
        """

        return self.pair

    def get_id(self):
        """
        Getter for interface id
        """

        return self.id

    def get_name(self):
        """
        Getter for getting name of interface
        """

        return self.name

    def _set_namespace(self, namespace):
        """
        Setter for the namespace associated 
        with the interface

        :param namespace: The namespace where the interface is installed
        :type namespace: Namespace
        """

        self.namespace = namespace

    def get_namespace(self):
        """
        Getter for the namespace associated 
        with the interface
        """

        return self.namespace

    def get_address(self):
        """
        Getter for the address associated
        with the interface
        """

        return self.address

    def set_address(self, address):
        """
        Assigns ip adress to an interface

        :param address: ip address to be assigned to the interface
        :type address: Address or string
        """

        if type(address) == str:
            address = Address(address)

        if self.namespace.is_default() is False:
            engine.assign_ip(self.get_namespace().get_id(),
                             self.get_id(), address.get_addr())
            self.address = address
        else:
            # Create our own error class
            raise NotImplementedError(
                'You should assign the interface to node or router before assigning address to it.')

    def get_subnet(self):
        """
        Getter for the subnet to which the address belongs to
        """
        return self.address.get_subnet()

    def set_mode(self, mode):
        """
        Changes the mode of the interface

        :param mode: interface mode to be set
        :type mode: string
        """

        error_handling.type_verify('mode', mode, 'string', str)

        if mode == 'UP' or mode == 'DOWN':
            if self.namespace.is_default() is False:
                engine.set_interface_mode(
                    self.get_namespace().get_id(), self.get_id(), mode.lower())
            else:
                # Create our own error class
                raise NotImplementedError(
                    'You should assign the interface to node or router before setting it\'s mode')
        else:
            raise ValueError(
                mode+' is not a valid mode (it has to be either "UP" or "DOWN")')

    def get_qdisc(self):
        """
        Return the qdisc (if) set by the user.
        Note that this is the qdisc set inside
        the IFB.
        """

        if self.ifb is not None:
            for qdisc in self.ifb.qdisc_list:
                if qdisc.parent == '1:1' and qdisc.handle == '11:':
                    return qdisc
        else:
            return None

    def add_qdisc(self, qdisc, parent='root', handle='', **kwargs):
        """
        Add a qdisc (Queueing Discipline) to this interface

        :param qdisc: The qdisc which needs to be added to the interface
        :type qdisc: string
        :param dev: The interface to which the qdisc is to be added
        :type dev: Interface class
        :param parent: id of the parent class in major:minor form(optional)
        :type parent: string
        :param handle: id of the filter
        :type handle: string
        :param **kwargs: qdisc specific paramters 
        :type **kwargs: dictionary
        """

        # TODO: Verify type of **kwargs

        # NOTE: Not necessary since API is not exposed to User for now
        error_handling.type_verify('qdisc', qdisc, 'string', str)
        error_handling.type_verify('parent', parent, 'string', str)
        error_handling.type_verify('handle', handle, 'string', str)

        self.qdisc_list.append(traffic_control.Qdisc(
            self.namespace.get_id(), self.get_id(), qdisc, parent, handle, **kwargs))

        # Add qdisc to TopologyMap
        TopologyMap.add_qdisc(self.namespace.get_id(),
                              self.get_id(), qdisc, handle, parent=parent)

        return self.qdisc_list[-1]

    def delete_qdisc(self, handle):
        """
        Delete qdisc (Queueing Discipline) from this interface

        :param handle: Handle of the qdisc to be deleted
        :type handle: string
        """

        # TODO: Handle this better by using the destructor in traffic-control
        counter = 0
        for qdisc in self.qdisc_list:
            if qdisc.handle == handle:
                engine.delete_qdisc(qdisc.namespace_id,
                                    qdisc.dev_id, qdisc.parent, qdisc.handle)
                TopologyMap.delete_qdisc(
                    self.namespace.get_id(), self.get_id(), handle)
                self.qdisc_list.pop(counter)
                break
            counter += 1

    def add_class(self, qdisc, parent='root', classid='', **kwargs):
        """
        Create an object that represents a class

        :param qdisc: The qdisc which needs to be added to the interface
        :type qdisc: string
        :param parent: id of the parent class in major:minor form(optional)
        :type parent: string
        :param classid: id of the class
        :type classid: string
        :param **kwargs: class specific paramters 
        :type **kwargs: dictionary
        """

        # TODO: Verify type of kwargs

        error_handling.type_verify('qdisc', qdisc, 'string', str)
        error_handling.type_verify('parent', parent, 'string', str)
        error_handling.type_verify('classid', classid, 'string', str)

        self.class_list.append(traffic_control.Class(
            self.namespace.get_id(), self.get_id(), qdisc, parent, classid, **kwargs))

        return self.class_list[-1]

    def add_filter(self, priority, filtertype, flowid, protocol='ip', parent='root', handle='',  **kwargs):
        """
        Design a Filter to assign to a Class or Qdisc

        :param protocol: protocol used
        :type protocol: string
        :param priority: priority of the filter
        :type priority: int
        :param filtertype: one of the available filters
        :type filtertype: string
        :param flowid: classid of the class where the traffic is enqueued 
                       if the traffic passes the filter
        :type flowid: Class
        :param parent: id of the parent class in major:minor form(optional)
        :type parent: string
        :param handle: id of the filter
        :type handle: string
        :param filter: filter parameters
        :type filter: dictionary
        :param **kwargs: filter specific paramters 
        :type **kwargs: dictionary
        """

        # TODO: Verify type of parameters
        # TODO: Reduce arguements to the engine functions by finding parent and handle automatically

        self.filter_list.append(traffic_control.Filter(self.namespace.get_id(), self.get_id(), protocol,
                                                       priority, filtertype, flowid, parent, handle, **kwargs))

        return self.filter_list[-1]

    def _create_and_mirred_to_ifb(self, dev_name):
        """
        Creates a IFB for the interface so that a Qdisc can be installed on it
        Mirrors packets to be sent out of the interface first to itself (IFB)
        Assumes the interface has already invoked _set_structure()

        :param dev_name: The interface to which the ifb was added
        :type dev_name: string
        """

        self.ifb = Interface('ifb-' + dev_name)
        engine.create_ifb(self.ifb.get_id())

        # Add ifb to namespace
        self.namespace._add_interface(self.ifb)

        # Set interface up
        self.ifb.set_mode('UP')

        default_route = {
            'default': '1'
        }

        # TODO: find how to set a good bandwitdh
        default_bandwidth = {
            'rate': '1024mbit'
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
            'dev': self.ifb.get_id()
        }

        # NOTE: Use Filter API
        engine.add_filter(self.namespace.get_id(), self.get_id(
        ), 'ip', '1', 'u32', parent='1:', **action_redirect)

    def _set_structure(self):
        """
        Sets a proper sturcture to the interface by creating htb class with default bandwidth and
        a netem qdisc as a child.
        (default bandwidth = 1024mbit) 

        """

        self.set_structure = True

        default_route = {
            'default': '1'
        }

        self.add_qdisc('htb', 'root', '1:', **default_route)

        # TODO: find how to set a good bandwitdh
        default_bandwidth = {
            'rate': '1024mbit'
        }

        self.add_class('htb', '1:', '1:1', **default_bandwidth)

        self.add_qdisc('netem', '1:1', '11:')

    def set_min_bandwidth(self, min_rate):
        """
        Sets a minimum bandwidth for the interface
        It is done by adding a htb qdisc and a rate parameter to the class

        :param min_rate: The minimum rate that has to be set in kbit
        :type min_rate: string
        """

        # TODO: Check if there exists a delay and if exists, make sure it is handled in the right way
        # TODO: Check if this is a redundant condition
        # TODO: Let user set the unit

        error_handling.type_verify('min_rate', min_rate, 'str', str)

        if self.set_structure is False:
            self._set_structure()

        min_bandwidth_parameter = {
            'rate': min_rate
        }

        # TODO: Check the created API
        # TODO: This should be handled by self.change_class
        engine.change_class(self.namespace.get_id(), self.get_id(
        ), '1:', 'htb', '1:1', **min_bandwidth_parameter)

    def set_delay(self, delay):
        """
        Adds a delay to the link between two namespaces
        It is done by adding a delay in the interface

        :param delay: The delay to be added
        :type delay: str
        """

        # TODO: It is not intuitive to add delay to an interface
        # TODO: Make adding delay possible without bandwidth being set
        # TODO: Check if this is a redundant condition
        # TODO: Let user set the unit

        error_handling.type_verify('delay', delay, 'string', str)

        if self.set_structure is False:
            self._set_structure()

        delay_parameter = {
            'delay': delay
        }

        # TODO: This should be handled by self.change_qdisc
        # It could lead to a potential bug!
        engine.change_qdisc(self.namespace.get_id(), self.get_id(
        ), 'netem', '1:1', '11:', **delay_parameter)

    def set_qdisc(self, qdisc, min_rate, **kwargs):
        """
        Adds the Queueing algorithm to the interface
        :param qdisc: The Queueing algorithm to be added
        :type qdisc: string
        
        TODO: Add doc for min_rate
        """

        # TODO: Don't use this API directly. If it used,
        # then the bandwidth should be same as link bandwidth
        # (A temporary bug fix is causing this issue. Look for
        # a permanent solution)
        # TODO: Check if this is a redundant condition

        error_handling.type_verify('qdisc', qdisc, 'string', str)

        if self.set_structure is False:
            self._set_structure()

        if self.ifb is None:
            self._create_and_mirred_to_ifb(self.name)

        min_bandwidth_parameter = {
            'rate': min_rate
        }

        engine.change_class(self.namespace.get_id(), self.ifb.get_id(
        ), '1:', 'htb', '1:1', **min_bandwidth_parameter)

        self.ifb.delete_qdisc('11:')
        self.ifb.add_qdisc(qdisc, '1:1', '11:', **kwargs)

    def set_attributes(self, bandwidth, delay, qdisc=None, **kwargs):
        """
        Add attributes bandwidth, delay and qdisc to interface

        :param bandwidth: Packet outgoing rate
        :type delay: string
        :param delay: Delay before packet is sent out
        :type delay: string
        :param qdisc: The Queueing algorithm to be added to interface
        :type qdisc: string
        """

        self.set_min_bandwidth(bandwidth)
        self.set_delay(delay)

        if qdisc is not None:
            self.set_qdisc(qdisc, bandwidth, **kwargs)


class Veth:
    """
    Handle creation of Veth pairs
    """

    def __init__(self, ns1, ns2, interface1_name, interface2_name):
        """
        Constructor to create a veth pair between
        `interface1_name` and `interface2_name`

        :param ns1: Namespace to which interface1 belongs to
        :type ns1: Namespace
        :param ns2: Namespace to which interface2 belongs to
        :type ns2: Namespace
        :param interface1_name: Name for interface1 (an endpoint of veth)
        :type interface1_name: string
        :param interface1_name: Name for interface2 (other endpoint of veth)
        :type interface1_name: string
        """

        self.interface1 = Interface(interface1_name)
        self.interface2 = Interface(interface2_name)

        self.interface1._set_pair(self.interface2)
        self.interface2._set_pair(self.interface1)

        # Create the veth
        engine.create_veth(self.interface1.get_id(), self.interface2.get_id())

    def _get_interfaces(self):
        """
        Get tuple of endpoint interfaces
        """

        return (self.interface1, self.interface2)


def connect(ns1, ns2, interface1_name='', interface2_name=''):
    """
    Connects two namespaces

    :param ns1, ns2: namespaces part of a connection
    :type ns1, ns2: Namespace 
    :return: A tuple containing two interfaces
    :r_type: (Interface, Interface)
    """

    error_handling.type_verify('ns1', ns1, 'Namespace', [Node, Router])
    error_handling.type_verify('ns2', ns2, 'Namespace', [Node, Router])
    error_handling.type_verify(
        'interface1_name', interface1_name, 'string', str)
    error_handling.type_verify(
        'interface2_name', interface2_name, 'string', str)

    # Create 2 interfaces

    if interface1_name == '' and interface2_name == '':
        connections = _number_of_connections(ns1, ns2)
        interface1_name = ns1.get_name() + '-' + ns2.get_name() + '-' + str(connections)
        interface2_name = ns2.get_name() + '-' + ns1.get_name() + '-' + str(connections)

    veth = Veth(ns1, ns2, interface1_name, interface2_name)
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
    This function gives the number of connections between the two namespaces

    :param ns1, ns2: Namespaces between which connections are needed
    :type ns1, ns2: Namespace
    :return: Number of connections between the two namespaces
    :r_tpye: int
    """

    connections = 0

    if len(ns1.interface_list) > len(ns2.interface_list):
        ns1, ns2 = ns2, ns1

    for interface in ns1.interface_list:
        if interface.get_pair().get_namespace() == ns2:
            connections = connections + 1

    return connections
