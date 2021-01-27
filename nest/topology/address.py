# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Handles addresses of interfaces"""

import ipaddress
from ipaddress import ip_address, IPv6Address


class Address:
    """Validate address.

    TODO: Untested for IPv6
    """

    def __init__(self, addr_str):
        """
        The constructor validates the entered IP address.

        Parameters
        ----------
        addr_str : str
            The string representing the address
        """

        if addr_str.isupper():  # A special string in place of address
            if addr_str == "DEFAULT":
                self.ip_addr = addr_str.lower()
            else:
                raise ValueError(
                    addr_str + " is not a special IP string. Perhaps you meant DEFAULT?"
                )
        elif "/" in addr_str:  # An interface address
            # raises exception in invalid case
            ipaddress.ip_interface(addr_str)
            self.ip_addr = addr_str
        else:  # An IP address
            # raises exception in invalid case
            ipaddress.ip_address(addr_str)
            self.ip_addr = addr_str + "/32"

    def get_addr(self, with_subnet=True):
        """Getter for ip_addr

        Parameters
        ----------
        with_subnet :
             (Default value = True)

        Returns
        -------
        str
            IP address as string
        """
        if with_subnet:
            return self.ip_addr

        return self.ip_addr.split("/")[0]

    def get_subnet(self):
        """Get the subnet of the given address"""
        if self.ip_addr == "default":
            raise Exception("default address cannot have a subnet")
        interface = ipaddress.ip_interface(self.ip_addr)
        return interface.network.compressed

    def is_subnet(self):
        """Check if the address is a subnet or not"""
        if self.ip_addr == "default":
            return False
        if self.ip_addr == self.get_subnet():
            return True
        return False

    def is_ipv6(self):
        """
        Check if the address is IPv6 or not

        Note: This takes care of 'DEFAULT' also
        """
        check_addr = self.ip_addr.split("/")[0]
        if isinstance(ip_address(check_addr), IPv6Address):
            return True
        return False

    def __repr__(self):
        classname = self.__class__.__name__
        return f"{classname}({self.ip_addr!r})"


class Subnet:
    """For generating sequential addresses in a subnet

    NOTE: Supported only for IPv4 addresses
    """

    def __init__(self, addr_str):
        address = Address(addr_str)

        if address.is_subnet():
            self._net_addr = ipaddress.ip_network(addr_str)
        else:
            raise ValueError("Parameter is not a subnet/network address")

        self._counter = 0

    def get_next_addr(self):
        """Get next address in sequence in the subnet"""
        self._counter += 1
        try:
            address = self._net_addr[self._counter]
        except IndexError as err:
            raise ValueError(
                "All the addresses for the network have been exhausted"
            ) from err
        return Address(address.compressed + "/" + str(self._net_addr.prefixlen))

    @property
    def counter(self):
        """Getter for counter"""
        return self._counter

    @property
    def network_address(self):
        """Getter for network address"""
        return self._net_addr

    def __repr__(self):
        classname = self.__class__.__name__
        return f"{classname}({self._net_addr!r})"
