# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# Handles addresses of interfaces
import ipaddress


class Address:
    """
    Validate address.

    TODO: Untested for IPv6
    """

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
                raise ValueError(
                    addr_str+' is not a special IP string. Perhaps you meant DEFAULT?')
        elif '/' in addr_str:       # An interface address
            # raises exception in invalid case
            ipaddress.ip_interface(addr_str)
            self.ip_addr = addr_str
        else:                       # An IP address
            # raises exception in invalid case
            ipaddress.ip_address(addr_str)
            self.ip_addr = addr_str+'/32'

    def get_addr(self, with_subnet=False):
        """
        Getter for ip_addr
        """

        if with_subnet:
            return self.ip_addr
        else:
            return self.ip_addr.split('/')[0]

    def get_subnet(self):
        """
        Get the subnet of the given address
        """

        interface = ipaddress.ip_interface(self.ip_addr)
        return interface.network.compressed

    def is_subnet(self):
        """
        Check if the address is a subnet or not
        """

        try:
            ipaddress.ip_network(self.ip_addr)
        except ValueError:
            return False
        return True


class Subnet:
    """
    For generating sequential addresses in a subnet

    NOTE: Supported only for IPv4 addresses
    """

    def __init__(self, addr_str):

        if '/' in addr_str:
            self.net_addr = ipaddress.ip_network(addr_str)
            self.counter = 0

    def get_next_addr(self):
        """
        Get next address in sequence in the subnet
        """

        self.counter += 1
        address = self.net_addr[self.counter]
        return Address(address.compressed + '/' + str(self.net_addr.prefixlen))
