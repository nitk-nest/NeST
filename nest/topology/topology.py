# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# Define network topology creation helpers
from .address import Address
from .. import engine
from . import error_handling
from .id_generator import ID_GEN
from ..configuration import Configuration
from . import traffic_control

class Namespace:
    """
    Base namespace class which is inherited by `Node` and `Router` classes
    """

    def __init__(self, ns_name = ''):
        """
        Constructor to initialize an unique id, name and a empty
        list of interfaces for the namespace

        :param ns_name: The name of the namespace to be created
        :type ns_name: string
        """


        if(ns_name != ''):
            # Creating a variable for the name
            self.name = ns_name
            self.id = ID_GEN.get_id(ns_name)

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
        """
        Get the (unique) id of the namespace
        """

        return self.id

    def get_name(self):
        """
        Get the (user-assigned) name of the namespace
        """

        return self.name

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
        
        engine.add_route(self.id, dest_addr.get_addr(without_subnet=True), next_hop_addr.get_addr(without_subnet=True), 
            via_interface.get_id())
        
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

        Configuration(self, "NODE")
    
    def enable_ip_forwarding(self):
        """
        Enable IP forwarding in Node.
        This gives flexibility to user to use a 
        Node as a Router.
        """

        engine.en_ip_forwarding(self.id)

    def install_server(self):
        """
        Install server on the node
        """

        Configuration._add_server(self)

    def send_packets_to(self, dest_addr):
        """
        Send packets from the node to `dest_addr`

        :param dest_addr: Address to send packets to
        :type dest_addr: Address or string
        """

        if type(dest_addr) == str:
            dest_addr = Address(dest_addr)

        Configuration._add_client(self)
        Configuration._set_destination(self, dest_addr.get_addr(without_subnet=True))
    
    def add_stats_to_plot(self, stat):
        """
        :param stat: statistic to be plotted
        :type stat: string
        """

        Configuration._add_stats_to_plot(self, stat)

class Router(Namespace):
    """
    This class represents the intermediate routers in a networks. It inherits 
    the Namespace class
    """

    def __init__(self, router_name):

        Namespace.__init__(self, router_name)

        # Add Rounter to configuration
        Configuration(self, "ROUTER")

        # Enable forwarding
        engine.en_ip_forwarding(self.id)

    def add_stats_to_plot(self, stat):
        """
        :param stat: statistic to be plotted
        :type stat: string
        """

        Configuration._add_stats_to_plot(self, stat)

class Interface:
    
    def __init__(self, interface_name, pair = ''):

        # Generate a unique interface id
        """
        name is only used to display it to the user
        id is the actual backend name
        namespace is of namespace class and not a string
        pair is another object of Interface class to which this is connected

        set_structure tells us if ifb, a default qdisc, netem and htb are added
        ifb is an object of interface class which tells the ifb associated with this interface

        qdisc_list, class_list, filter_list gives a list of all those as respective classes 
        """

        self.name = interface_name
        self.id = ID_GEN.get_id(interface_name)
        self.namespace = Namespace()
        self.pair = None
        self.address = None

        self.set_structure = False
        self.ifb = None

        # NOTE: These lists required?
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
            
        """

        return self.pair

    def get_id(self):
        """
        Getter for interface id
        """

        return self.id

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

        self.qdisc_list.append(traffic_control.Qdisc(self.namespace.get_id(), self.get_id(), qdisc, parent, handle, **kwargs))


        return self.qdisc_list[-1]

    def add_class(self, qdisc, parent = 'root', classid = '', **kwargs):
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

        self.class_list.append(traffic_control.Class(self.namespace.get_id(), self.get_id(), qdisc, parent, classid, **kwargs))

        return self.class_list[-1]


    def add_filter(self, priority, filtertype, flowid, protocol = 'ip', parent='root', handle = '',  **kwargs):
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

        #TODO: Reduce arguements to the engine functions by finding parent and handle automatically
        self.filter_list.append(traffic_control.Filter(self.namespace.get_id(), self.get_id(), protocol, priority, filtertype, flowid, parent, handle, **kwargs))

        return self.filter_list[-1]

    def _create_ifb(self, dev_name):
        """
        Creates a IFB for the interface so that a Qdisc can be installed on it

        :param dev_name: The interface to which the ifb was added
        :type dev_naem: string

        """

        self.ifb = Interface('ifb-' + dev_name)
        self.ifb._set_namespace(self.namespace)
        engine.setup_ifb(self.ifb.get_namespace().get_id(), self.ifb.get_id())

    def _set_structure(self):
        """
        Sets a proper sturcture to the interface by creating htb class with default bandwidth and
        a netem qdisc as a child. It also adds an IFB mirred action and a qdisc can be added to it
        (default bandwidth = 1024mbit) 

        """
        
        self.set_structure = True

        self._create_ifb(self.id)

        default_route = {
            'default' : '1'
        }

        self.ifb.add_qdisc('htb', 'root', '1:', **default_route)
        
        self.add_qdisc('htb', 'root', '1:', **default_route)

        # TODO: find how to set a good bandwitdh
        default_bandwidth = {
            'rate' : '1024mbit'
        }

        self.ifb.add_class('htb', '1:', '1:1', **default_bandwidth)

        self.add_class('htb', '1:', '1:1', **default_bandwidth)

        self.ifb.add_qdisc('pfifo', '1:1', '11:')

        self.add_qdisc('netem', '1:1', '11:')

        action_redirect = {
            'match' : 'u32 0 0',  # from man page examples
            'action' : 'mirred',
            'egress' : 'redirect',
            'dev' : self.ifb.get_id()
        }

        # NOTE: Use Filter API
        engine.add_filter(self.namespace.get_id(), self.get_id(), 'ip', '1', 'u32', parent = '1:', **action_redirect)

    def set_min_bandwidth(self, min_rate):
        """
        Sets a minimum bandwidth for the inteeface
        It is done by adding a htb qdisc and a rate parameter to the class

        :param min_rate: The minimum rate that has to be set in kbit
        :type min_rate: int

        """

        # TODO: Check if there exists a delay and if exists, make sure it is handled in the right way
        # TODO: Check if this is a redundant condition
        # TODO: Let user set the unit

        if self.set_structure is False:
            self._set_structure()

        min_bandwidth_parameter = {
            'rate' : str(min_rate) + 'kbit'
        }

        # TODO: Check the created API
        engine.change_class(self.namespace.get_id(), self.get_id(), '1:', 'htb', '1:1', **min_bandwidth_parameter)


        # engine.exec_subprocess('ip netns exec {} tc class change dev {} parent {}' \
        #     ' classid {} htb rate {}'.format(self.get_namespace().get_id(), self.get_id(), 
        #     '1:', '1:1', min_rate))

    def set_delay(self, delay):
        """
        Adds a delay to the link between two namespaces
        It is done by adding a delay in the interface

        :param delay: The delay to be added in milliseconds
        :type delay: int

        """

        # TODO: It is not intuitive to add delay to an interface
        # TODO: Make adding delay possible without bandwidth being set
        # TODO: Check if this is a redundant condition
        # TODO: Let user set the unit

        if self.set_structure is False:
            self._set_structure()

        delay_parameter = {
            'delay' : str(delay) + 'ms'
        }

        engine.change_qdisc(self.namespace.get_id(),self.get_id(), 'netem', '1:1', '11:', **delay_parameter)

        # TODO: Verify created API
        # engine.exec_subprocess('ip netns exec {} tc qdisc change dev {} parent {}' \
        #     ' handle {} netem delay {}'.format(self.get_namespace().get_id(), self.get_id(), 
        #     '1:1', '11:', delay))

        
    def set_qdisc(self, qdisc, **kwargs):
        """
        Adds the Queueing algorithm to the interface
        :param qdisc: The Queueing algorithm to be added
        :type qdisc: string
        """
        # TODO: Check if this is a redundant condition
        if self.set_structure is False:
            self._set_structure()

        engine.change_qdisc(self.namespace.get_id(), self.ifb.get_id(), qdisc, '1:1', '11:', **kwargs)

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



    def get_interfaces(self):
        """
        Get tuple of endpoint interfaces
        """

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

    veth = Veth(ns1, ns2, interface1_name, interface2_name)
    (int1, int2) = veth.get_interfaces()

    ns1.add_interface(int1)
    ns2.add_interface(int2)

    # Set the proper structure for the veth
    int1._set_structure()
    int2._set_structure()

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