# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019 NITK Surathkal

from .engine import assign_ip, set_interface_mode
from .address import Address

class Interface:
    
    def __init__(self, namespace):

        # generate a unique interface id
        self.id = id(self)
        self.namespace = namespace

    def get_id(self):
        """
        getter for interface id
        """

        return self.id

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
            try:
                address = Address(address)
            except:
                # TODO: Raise a valid error
                pass
        
        assign_ip(self.get_namespace(), self.get_id(),address.get_addr())

    def set_mode(self, mode):
        """
        Changes the mode of the interface

        :param mode: interface mode to be set
        :type mode: string
        """

        # TODO: Check if the mode is valid
        set_interface_mode(self.get_namespace, self.get_id, mode)
    





