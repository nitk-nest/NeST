# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# Define network topology creation helpers
from .address import Address
from . import engine
from . import error_handling
from .id_generator import ID_GEN
from .configuration import Configuration
from . import traffic_control

class Namespace:
    """
    Base namespace class which is inherited by `Node` and `Router` classes
    """

    def __init__(self, ns_name = ''):
        """
        Constructor to initialize an unique id for the namespace
        and an empty list

        :param ns_name: The name of the namespace to be created
        :type ns_name: string
        """


        if(ns_name != ''):
            # Creating a variable for the name
            self.name = ns_name
            self.id = ID_GEN.get_id()

            # Create a namespace with the name
            engine.create_ns(self.id)
        else:
            self.id = 'default'

        # Initialize an empty list of interfaces to keep track of interfaces on it
        self.interface_list = []

    def is_default(self):
        """
        Checks if the namespace is same as the default
        namespace.
        """

        if self.id == 'default':
            return True
        else:
            return False

    def get_id(self):

        return self.id

    def add_route(self, dest_addr, next_hop_addr, via_interface):
        """
        Adds a route to the routing table of the namespace with
        the given parameters

        :param dest_addr: Destination ip address of the namespace
        :type dest_addr: Address or string
        :param next_hop_address: ip address of the next hop router
        :type next_hop_address: Address or string
        :param via_interface: interface on the namespace used to route
        :type via_interface: Interface
        """

        if type(dest_addr) == str:
            dest_addr = Address(dest_addr)

        if type(next_hop_addr) == str:
            next_hop_addr = Address(next_hop_addr)
        
        engine.add_route(self.id, dest_addr.get_abs_addr(), next_hop_addr.get_abs_addr(), via_interface.get_id())
        
    def add_interface(self, interface):
        """
        Adds an interface to the namespace

        :param interface: Interface to be added to the namespace
        :type interface: Interface
        """

        self.interface_list.append(interface)
        interface._set_namespace(self)
        engine.add_int_to_ns(self.get_id(), interface.get_id())


class Node(Namespace):
    """
    This class represents the end devices on a network. It inherits
    the Namespace class
    """

    def __init__(self, node_name):

        Namespace.__init__(self, node_name)
        
        # Add node to configuration
        Configuration(self, "Node")

class Router(Namespace):
    """
    This class represents the intermediate routers in a networks. It inherits 
    the Namespace class
    """

    def __init__(self, router_name):

        Namespace.__init__(self, router_name)

        # Add Rounter to configuration
        Configuration(self, "Router")

        # Enable forwarding
        engine.en_ip_forwarding(self.id)

class Interface:
    
    def __init__(self, interface_name, pair = ''):

        # Generate a unique interface id
        self.name = interface_name
        self.id = ID_GEN.get_id()
        self.namespace = Namespace()
        self.pair = None
        self.address = None
        self.qdisc_list = []
        self.class_list = []

    def _set_pair(self, interface):
        """
        setter for the other end of the interface that it is connected to
        :param interface_name: The interface to which this interface is connected to
        :type interface_name: Interface
        """

        self.pair = interface

    def get_pair(self):
        """
        getter for the interface to which this interface is connected to
        :return: Interface to which this interface is connected to
        :r_type: Interface
        """

        return self.pair

    def get_id(self):
        """
        getter for interface id
        """

        return self.id

    def _set_namespace(self, namespace):
        """
        setter for the namespace associated 
        with the interface

        :param namespace: The namespace where the interface is installed
        :type namespace: Namespace
        """

        self.namespace = namespace

    def get_namespace(self):
        """
        getter for the namespace associated 
        with the interface
        """

        return self.namespace
    
    def get_address(self):
        """
        getter for the address associated
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
            engine.assign_ip(self.get_namespace().get_id(), self.get_id(), address.get_addr())
            self.address = address
        else:
            # Create our own error class
            raise NotImplementedError('You should assign the interface to node or router before assigning address to it.')

    def set_mode(self, mode):
        """
        Changes the mode of the interface

        :param mode: interface mode to be set
        :type mode: string
        """

        if mode == 'UP' or mode == 'DOWN':
            if self.namespace.is_default() is False:
                engine.set_interface_mode(self.get_namespace().get_id(), self.get_id(), mode.lower())
            else:
            # Create our own error class
                raise NotImplementedError('You should assign the interface to node or router before setting it\'s mode')
        else:
             raise ValueError(mode+' is not a valid mode (it has to be either "UP" or "DOWN")')

    def add_qdisc(self, qdisc, parent = 'root', handle = '', **kwargs):
        """
        Constructor to add a qdisc (Queueing Discipline) to this interface

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

        self.qdisc_list.append(traffic_control.Qdisc(self.get_id(), self.namespace.get_id(), qdisc, parent, handle, **kwargs))

    def add_class(self, qdisc, parent = 'root', classid = '', **kwargs):
        """
        Constructor to create an object that represents a class

        :param dev_id: The id of the interface to which the qdisc is to be added
        :type dev_id: String
        :param namespace_id: The id of the namespace that the device belongs to
        :type namespace_id: String
        :param qdisc: The qdisc which needs to be added to the interface
        :type qdisc: string
        :param parent: id of the parent class in major:minor form(optional)
        :type parent: string
        :param classid: id of the class
        :type classid: string
        :param **kwargs: class specific paramters 
        :type **kwargs: dictionary
        """

        self.class_list.append(traffic_control.Class(self.get_id(), self.namespace.get_id(), qdisc, parent, classid, **kwargs))


class Veth:
    """
    Handle creation of Veth pairs
    """

    def __init__(self, interface1_name, interface2_name):

        self.interface1 = Interface(interface1_name)
        self.interface2 = Interface(interface2_name)

        self.interface1._set_pair(self.interface2)
        self.interface2._set_pair(self.interface1)

        # Create the veth
        engine.create_veth(self.interface1.get_id(), self.interface2.get_id())

    def get_interfaces(self):

        return (self.interface1, self.interface2)


def connect(ns1, ns2, interface1_name = '', interface2_name = ''):
    """
    Connects two namespaces

    :param ns1, ns2: namespaces part of a connection
    :type ns1, ns2: Namespace 
    :return: A tuple containing two interfaces
    :r_type: (Interface, Interface)
    """
    
    # Create 2 interfaces

    if interface1_name == '' and interface2_name == '':
        connections = number_of_connections(ns1, ns2)
        interface1_name = ns1.get_id() + '-' + ns2.get_id() + '-' + str(connections)
        interface2_name = ns2.get_id() + '-' + ns1.get_id() + '-' + str(connections)

    veth = Veth(interface1_name, interface2_name)
    (int1, int2) = veth.get_interfaces()

    ns1.add_interface(int1)
    ns2.add_interface(int2)

    int1.set_mode('UP')
    int2.set_mode('UP')

    return (int1, int2)

def number_of_connections(ns1, ns2):
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