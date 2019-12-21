# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019 NITK Surathkal

# Define network topology creation helpers
from .address import Address
import engine
from .interface import Interface, Veth

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
            self.id = id(self)

            # Create a namespace with the unique id
            engine.create_ns(self.id)
        else:
            self.id = 'default'

        # Initialize an empty list to keep track of
        # Interfaces on it
        self.interfaces = []

    def is_default(self):

        if self.id == 'default':
            return True
        else:
            return False

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

