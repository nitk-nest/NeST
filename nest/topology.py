# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019 NITK Surathkal

# Define network topology creation helpers
from .address import Address
from .engine import add_route
from .engine import en_ip_forwarding
from .engine import create_ns

class Namespace:
    """
    Base namespace class which is inherited by `Node` and `Router` classes
    """

    def __init__(self):
        """
        Constructor to initialize an unique id for the namespace
        and an empty list
        """

        # generate a unique id for the namespace
        self.id = id(self)

        # create a namespace with the unique id
        create_ns(self.id)

        # initialize an empty list to keep track of
        # interfaces on it
        self.interfaces = []

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
            try:
                dest_addr = Address(dest_addr)
            except: 
                # TODO: Raise a valid error
                pass

        if type(next_hop_addr == 'Address'):
            try:
                next_hop_addr = Address(next_hop_addr)
            except:
                # TODO: Raise a valid errot
                pass

        
        add_route(self.id, dest_addr.get_addr(), next_hop_addr.get_addr(), via_interface.get_id())
        

class Node(Namespace):

    def __init__(self):
        pass
        # Create namespace in iproute2

class Router(Namespace):

    def __init__(self):

        Namespace.__init__(self)

        # Enable forwarding
        en_ip_forwarding(self.id)
