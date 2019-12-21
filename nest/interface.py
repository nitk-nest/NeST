# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019 NITK Surathkal

from .address import Address
from .topology import Namespace
import engine

class Interface:
    
    def __init__(self):

        # Generate a unique interface id
        self.id = id(self)
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
    
    def assign_address(self, address):
        """
        Assigns ip adress to an interface

        :param address: ip address to be assigned to the interface
        :type address: Address or string
        """
   
        if type(address) == 'str':
            address = Address(address)
            
        if self.namespace.is_default() is False:
            engine.assign_ip(self.get_namespace(), self.get_id(), address.get_addr())
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
                engine.set_interface_mode(self.get_namespace, self.get_id, mode.to_lower())
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
