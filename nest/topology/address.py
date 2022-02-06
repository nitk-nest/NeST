# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""Handles addresses of interfaces"""

import ipaddress
from ipaddress import ip_address, IPv6Address, IPv4Address

from nest.input_validator.input_validator import input_validator


class Address:
    """
    Validate IP addresses and provide some basic APIs
    to obtain information about the IP address.

    """

    @input_validator
    def __init__(self, addr_str: str):
        """
        The constructor validates the entered IP address.

        Parameters
        ----------
        addr_str : str
            The string representing the address
        """

        # Check if a "special" string is passed
        if addr_str == "DEFAULT":  # A special string in place of address
            self.ip_addr = addr_str.lower()
            return

        # Split address and prefix_len
        _addr_str, _prefix_len = self._split_address_and_prefix_length(addr_str)

        # if IPv4 address
        # expected format from user => (10.0.0.0/24 or 10.0.0.0)
        if self._is_ipv4(_addr_str):
            self.ip_addr = self._get_ipv4_address(_addr_str, _prefix_len)

        # if IPv4-Mapped IPv6 address
        # expected format from user => (::FFFF:10.0.0.0/122 or ::FFFF:10.0.0.0)
        elif self._is_ipv4_mapped_ipv6(_addr_str):
            self.ip_addr = self._get_ipv4_mapped_ipv6_address(_addr_str, _prefix_len)

        # if IPv6 address
        # expected format from user => (2a0:101::/122 or 2a0:101::)
        elif self._is_ipv6(_addr_str):
            self.ip_addr = self._get_ipv6_address(_addr_str, _prefix_len)

        else:
            raise ValueError(addr_str + " is not a valid IP address")

    @staticmethod
    def allowed_type_cast():
        """
        Indicate str can be typecasted into Address type
        """
        return [str]

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

    def _split_address_and_prefix_length(self, addr_str):
        """
        Split address and prefix length

        Parameters
        ----------
        addr_str : str
            The string representing the address

        Returns
        -------
        tuple
            addr_str :str
            prefix_len : int

        """
        # raises exception in invalid case
        ipaddress.ip_interface(addr_str)

        if "/" in addr_str:
            addr_str = addr_str.split("/")
            prefix_len = int(addr_str[1])
            addr_str = addr_str[0]
        else:
            prefix_len = None

        return addr_str, prefix_len

    def _is_ipv4(self, addr_str):
        """
        Check if the address without prefix length is IPv4 or not

        Parameters
        ----------
        addr_str : str
            The string representing the address

        """
        return isinstance(ip_address(addr_str), IPv4Address)

    def _is_ipv4_mapped_ipv6(self, addr_str):
        """
        Check if the address without prefix length is IPv4-mapped IPv6 or not

        Parameters
        ----------
        addr_str : str
            The string representing the address

        """
        return ipaddress.IPv6Address(addr_str).ipv4_mapped is not None

    def _is_ipv6(self, addr_str):
        """
        Check if the address without prefix length is IPv6 or not

        Parameters
        ----------
        addr_str : str
            The string representing the address

        """
        return isinstance(ip_address(addr_str), IPv6Address)

    def _get_ipv4_address(self, addr_str, prefix_len):
        """
        Getter for IPv4 Address

        Parameters
        ----------
        addr_str : str
            The string representing the address
        prefix_len : int
            The prefix length

        Returns
        -------
        str
            IPv4 address as string

        """
        if prefix_len is None:
            prefix_len = 32
        addr_str = addr_str + "/" + str(prefix_len)
        return addr_str

    def _get_ipv4_mapped_ipv6_address(self, addr_str, prefix_len):
        """
        Getter for IPV4-mapped IPv6 Address

        Parameters
        ----------
        addr_str : str
            The string representing the address
        prefix_len : int
            The prefix length

        Returns
        -------
        str
            IPv4 address as string

        """
        addr_str = str(ipaddress.IPv6Address(addr_str).ipv4_mapped)
        # If the prefix length is empty or not valid (between 96 and 128), then it is set to 32.
        # Ipv4-mapped address has 128 bits. The IPv4 address takes the last 32 bits,
        # and therefore the first 96 (128-32) bits from the address are removed. Therefore
        # valid prefix length will be in between 96 and 128.
        if prefix_len is not None and prefix_len in range(97, 128):
            prefix_len = prefix_len - 96
        else:
            prefix_len = None
        return self._get_ipv4_address(addr_str, prefix_len)

    def _get_ipv6_address(self, addr_str, prefix_len):
        """
        Getter for IPv6 Address

        Parameters
        ----------
        addr_str : str
            The string representing the address
        prefix_len : int
            The prefix length

        Returns
        -------
        str
            IPv6 address as string

        """
        if prefix_len is None:
            prefix_len = "128"
        addr_str = addr_str + "/" + str(prefix_len)
        return addr_str

    def __repr__(self):
        classname = self.__class__.__name__
        return f"{classname}({self.ip_addr!r})"


class Subnet:
    """
    For generating sequential addresses in a subnet

    """

    @input_validator
    def __init__(self, address: Address):
        if address.is_subnet():
            self._net_addr = ipaddress.ip_network(address.get_addr())
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
