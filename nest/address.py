# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# Handles addresses of interfaces
import ipaddress

class Address:

    def __init__(self, addr_str):
        """
        :param addr_str: The string representing the address
                         The constructor validates the entered ip
                         address.
        :type add_str: String
        """
       
        # NOTE: This should also handle ipv6. Requires testing to confirm.

        if addr_str.isupper():      # A special string in place of address
            if addr_str == 'DEFAULT':
                self.ip_addr = addr_str.lower()
            else:
                raise ValueError(addr_str+' is not a special IP string. Perhaps you meant DEFAULT?')
        elif '/' in addr_str:       # An interface address
            ipaddress.ip_interface(addr_str)    # raises exception in invalid case
            self.ip_addr = addr_str
        else:                       # An IP address  
            ipaddress.ip_address(addr_str)      # raises exception in invalid case
            self.ip_addr = addr_str
    
    def get_addr(self):
        """
        getter for ip_addr
        """
        return self.ip_addr
