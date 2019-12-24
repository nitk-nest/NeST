# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019 NITK Surathkal

# Define network topology creation helpers
from .address import Address
from . import engine

class Namespace:
    """
    Base namespace class which is inherited by `Node` and `Router` classes
    """

    def __init__(self, default=False):
        """
        Constructor to initialize an unique id for the namespace
        and an empty list
        """

        if(default == False):
            # Generate a unique id for the namespace
            self.id = str(id(self))

            # Create a namespace with the unique id
            engine.create_ns(self.id)
        else:
            self.id = 'default'

        # Initialize an empty list to keep track of
        # Interfaces on it
        # self.interfaces = []

    def is_default(self):

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

        if type(dest_addr) == 'str':
            dest_addr = Address(dest_addr)

        if type(next_hop_addr == 'Address'):
            next_hop_addr = Address(next_hop_addr)
        
        engine.add_route(self.id, dest_addr.get_addr(), next_hop_addr.get_addr(), via_interface.get_id())
        

class Node(Namespace):

    def __init__(self):

        Namespace.__init__(self)

class Router(Namespace):

    def __init__(self):

        Namespace.__init__(self)

        # Enable forwarding
        engine.en_ip_forwarding(self.id)

class Interface:
    
    def __init__(self):

        # Generate a unique interface id
        self.id = str(id(self))
        self.namespace = Namespace(default=True)

    def get_id(self):
        """
        getter for interface id
        """

        return self.id

    def set_namespace(self, namespace):
        """
        setter for the namespace associated 
        with the interface
        """

        engine.add_int_to_ns(namespace.get_id(), self.id)
        self.namespace = namespace

    def get_namespace(self):
        """
        getter for the namespace associated 
        with the interface
        """

        return self.namespace
    
    def set_address(self, address):
        """
        Assigns ip adress to an interface

        :param address: ip address to be assigned to the interface
        :type address: Address or string
        """
   
        if type(address) == 'str':
            address = Address(address)
            
        if self.namespace.is_default() is False:
            engine.assign_ip(self.get_namespace().get_id(), self.get_id(), address.get_addr())
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


class Veth:

    def __init__(self):

        self.interface1 = Interface()
        self.interface2 = Interface()

        # Create the veth
        engine.create_veth(self.interface1.get_id(), self.interface2.get_id())

    def get_interfaces(self):

        return (self.interface1, self.interface2)

def connect(ns1, ns2):
    """
    Connect namespaces `ns1` and `ns2`
    """
    
    # Create 2 interfaces
    veth = Veth()
    (int1, int2) = veth.get_interfaces()
    
    int1.set_namespace(ns1)
    int2.set_namespace(ns2)

    int1.set_mode('UP')
    int2.set_mode('UP')

    return (int1, int2)

