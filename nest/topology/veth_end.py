# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""API related to creation of virtual ethernet devices in topology"""

import logging
import nest.config as config
import nest.global_variables as g_var
from nest import engine
from .device import Device
from .address import Address

logger = logging.getLogger(__name__)

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-branches


class VethEnd(Device):
    """
    This is the end of the veth created, to connect two devices

    Attributes
    ----------
    id : str
        This value is used by `engine` to create emulated interface
        entity
    node_id : str
        id of the Node to  which this Interface belongs
    address : str/Address
        IP address assigned to this interface
    bandwidth : str
        The bandwidth set to the device
    delay : str
        The delay set to the device
    """

    def __init__(self, name, node_id):
        """
        Constructor of VethEnd

        Parameters
        ----------
        name : str
            Name of the interface
        node_id : str
            Id of the node that the interface belongs to
        """

        super().__init__(name, node_id)
        self._ipv4_address = None
        self._ipv6_address = None
        self.bandwidth = None
        self.delay = None
        self._set_structure = False

        self._mtu = 1500
        self._is_mpls_enabled = False

    @property
    def address(self):
        """
        Getter for the address associated
        with the interface
        """
        return self.get_address()

    @address.setter
    def address(self, address):
        """
        Assigns IP address/addresses to an interface

        Parameters
        ----------
        address : Address or str or List of Address and/or str
            IP address to be assigned to the interface
        """
        # TODO: The below check is redundant since
        # input_validator check is run in Interface
        if isinstance(address, str):
            address = [Address(address)]
        elif isinstance(address, list):
            for i in range(len(address)):
                if isinstance(address[i], str):
                    address[i] = Address(address[i])
        else:
            address = [address]

        if self.node_id is None:
            # TODO: Create our own error class
            raise NotImplementedError(
                "You should assign the interface to node or router before assigning address to it."
            )

        if isinstance(self._ipv4_address, list):
            for addr in self._ipv4_address:
                engine.delete_ip(self.node_id, self.id, addr.get_addr())
            self._ipv4_address = None
        if isinstance(self._ipv6_address, list):
            for addr in self._ipv6_address:
                engine.delete_ip(self.node_id, self.id, addr.get_addr())
            self._ipv6_address = None
        for addr in address:
            engine.assign_ip(self.node_id, self.id, addr.get_addr())
            if addr.is_ipv6() is True:
                if self._ipv6_address is None:
                    self._ipv6_address = [addr]
                else:
                    self._ipv6_address.append(addr)
            else:
                if self._ipv4_address is None:
                    self._ipv4_address = [addr]
                else:
                    self._ipv4_address.append(addr)

        # Global variable to check if address is ipv6 or not for DAD check
        if self._ipv6_address is not None:
            g_var.IS_IPV6 = True

    def add_address(self, address):
        """
        Adds IP address to an interface

        Parameters
        ----------
        address : Address or str or list of Address and/or str
            IP address to be added to the interface
        """
        if isinstance(address, str):
            address = Address(address)
        elif isinstance(address, list):
            for i in range(len(address)):
                if isinstance(address[i], str):
                    address[i] = Address(address[i])

        if self.node_id is None:
            raise NotImplementedError(
                "You should assign the interface to node or router before assigning address to it."
            )

        if isinstance(address, list):
            for addr in address:
                engine.assign_ip(self.node_id, self.id, addr.get_addr())
                if addr.is_ipv6() is True:
                    if self._ipv6_address is None:
                        self._ipv6_address = [addr]
                    else:
                        self._ipv6_address.append(addr)
                else:
                    if self._ipv4_address is None:
                        self._ipv4_address = [addr]
                    else:
                        self._ipv4_address.append(addr)
        else:
            engine.assign_ip(self.node_id, self.id, address.get_addr())
            if address.is_ipv6() is True:
                if self._ipv6_address is None:
                    self._ipv6_address = [address]
                else:
                    self._ipv6_address.append(address)
            else:
                if self._ipv4_address is None:
                    self._ipv4_address = [address]
                else:
                    self._ipv4_address.append(address)

    def get_address(self, ipv4=True, ipv6=True, as_list=False):
        """
        Gets the required IP addresses for the interface

        Parameters
        ----------
        ipv4 : If set to true, the IPv4 address of the interface is returned (defaults to True)
        ipv6 : If set to true, the IPv6 address of the interface is returned (defaults to True)
        If both are True, both the addresses are returned
        Either ipv4 or ipv6 must be True
        as_list : Returns the address as a list if set to True and only one address is returned
        """

        if not (ipv4 or ipv6):
            raise ValueError("Either ipv4 or ipv6 argument must be True")
        ipv4_address, ipv6_address = self._ipv4_address, self._ipv6_address
        if not ipv4_address:
            ipv4_address = None
        if not ipv6_address:
            ipv6_address = None

        if not as_list:
            if ipv4 and ipv4_address and len(ipv4_address) == 1:
                ipv4_address = ipv4_address[0]
            if ipv6 and ipv6_address and len(ipv6_address) == 1:
                ipv6_address = ipv6_address[0]
        if not ipv6 or ipv6_address is None:
            return ipv4_address
        if not ipv4 or ipv4_address is None:
            return ipv6_address
        return (ipv4_address, ipv6_address)

    def del_address(self, address):
        """
        Delete IP address(es) from the interface

        Parameters
        ----------
        address : str or list
            IP address to be deleted from the interface
        """
        if isinstance(address, str):
            address = [Address(address)]
        elif isinstance(address, list):
            for i in range(len(address)):
                if isinstance(address[i], str):
                    address[i] = Address(address[i])
        else:
            address = [address]

        if self.node_id is None:
            raise NotImplementedError(
                "You should assign the interface to node or router before assigning address to it."
            )
        for addr in address:
            if addr.is_ipv6():
                found = -1
                for i in range(len(self._ipv6_address)):
                    if self._ipv6_address[i].get_addr() == addr.get_addr():
                        found = i
                        break
                if found > -1:
                    engine.delete_ip(self.node_id, self.id, addr.get_addr())
                    self._ipv6_address.pop(found)
                else:
                    raise NotImplementedError(
                        "Cannot delete an address that is not assigned."
                    )
            else:
                found = -1
                for i in range(len(self._ipv4_address)):
                    if self._ipv4_address[i].get_addr() == addr.get_addr():
                        found = i
                        break
                if found > -1:
                    engine.delete_ip(self.node_id, self.id, addr.get_addr())
                    self._ipv4_address.pop(found)
                else:
                    raise NotImplementedError(
                        "Cannot delete an address that is not assigned."
                    )
        if not self._ipv4_address:
            self._ipv4_address = None
        if not self._ipv6_address:
            self._ipv6_address = None

    def disable_ip_dad(self):
        """
        Disables Duplicate addresses Detection (DAD) for an interface.
        """
        engine.disable_dad(self.node_id, self._id)

    def enable_mpls(self):
        """
        Enables mpls input through the interface.
        Requires mpls kernel modules to be loaded.

        Run ``sudo modprobe mpls_iptunnel`` to load mpls modules.
        """
        if self.node_id is None:
            raise NotImplementedError(
                "You should assign the interface to node or router before enabling mpls"
            )

        engine.set_mpls_max_label_node(self.node_id, int(100000))

        if self._is_mpls_enabled is False:
            engine.enable_mpls_interface(self.node_id, self.id)
            self._is_mpls_enabled = True
            self.mtu = 1504

    def is_mpls_enabled(self):
        """
        Check if the interface has mpls enabled
        """
        return self._is_mpls_enabled

    @property
    def mtu(self):
        """
        Get the maximum transmit unit value for the interface
        """
        return self._mtu

    @mtu.setter
    def mtu(self, mtu_value):
        """
        Set the maximum transmit unit value for the interface
        Default is 1500 bytes.
        """
        if self._mtu != mtu_value:
            engine.set_mtu_interface(self.node_id, self.id, int(mtu_value))
            self._mtu = mtu_value
            logger.debug("MTU of interface %s set to %s", self.name, str(self.mtu))

    def set_structure(self):
        """
        Sets a proper structure to the interface by creating HTB class
        with default bandwidth and a netem qdisc as a child.
        HTB is used for setting bandwidth and netem is used for setting
        delay, packet corruption etc
        (default bandwidth = 1024mbit)
        """

        if self._set_structure is True:
            return

        self._set_structure = True

        default_route = {"default": "1"}

        # HTB is added since netem is a classless qdisc. So, htb class,
        # With netem as child is added
        self.add_qdisc("htb", "root", "1:", **default_route)

        # TODO: find how to set a good bandwidth
        default_bandwidth = {"rate": config.get_value("default_bandwidth")}

        self.add_class("htb", "1:", "1:1", **default_bandwidth)

        self.add_qdisc("netem", "1:1", "11:")

    def enable_offload(self, offload_name):
        """
        API for enabling offloads
        Parameters
        ----------
        offload_name : str
            The type of offload names that need to enable
        """
        if not isinstance(offload_name, list):
            offload_name = [offload_name]
        valid_offloads(offload_name)
        namespace_id = self.node_id
        interface_id = self.id
        for offload_type in offload_name:
            if engine.ethtool.enable_offloads(namespace_id, interface_id, offload_type):
                logger.debug(
                    "%s is enabled on interface %s",
                    offload_type,
                    self.name,
                )
            else:
                logger.error(
                    "%s is not enabled on interface %s",
                    offload_type,
                    self.name,
                )

    def disable_offload(self, offload_name):
        """
        API for disabling offloads
        Parameters
        ----------
        offload_name : str
            The type of offload names that need to disable
        """
        if not isinstance(offload_name, list):
            offload_name = [offload_name]
        valid_offloads(offload_name)
        namespace_id = self.node_id
        interface_id = self.id
        for offload_type in offload_name:
            if engine.ethtool.disable_offloads(
                namespace_id, interface_id, offload_type
            ):
                logger.debug(
                    "%s is disabled on interface %s",
                    offload_type,
                    self.name,
                )
            else:
                logger.error(
                    "%s is not disabled on interface %s",
                    offload_type,
                    self.name,
                )


def valid_offloads(offload_name):
    """
    Check valid offloads

    Parameters
    -----------
    offload_name : str
        The offload name
    """
    offloads_list = ["tso", "gso", "gro"]
    for offload_type in offload_name:
        if not offload_type in offloads_list:
            logger.error("Invalid offload")
            raise ValueError(f"{offload_type} is not a valid offload")
