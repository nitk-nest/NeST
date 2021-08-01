# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""API related to creation of physical interfaces in topology"""

import logging
import nest.config as config
import nest.global_variables as g_var
from nest import engine
from nest.topology.device import Device
from .address import Address

logger = logging.getLogger(__name__)

# Max length of interface when Topology Map is disabled
# i.e. 'assign_random_names' is set to False in config
MAX_CUSTOM_NAME_LEN = 15

# pylint: disable=too-many-instance-attributes


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
    pair : Veth_end
        The other end of the veth pair
    bandwidth : str
        The bandwidth set to the device
    delay : str
        The delay set to the device
    """

    def __init__(self, name, node_id, pair):
        """
        Constructor of VethEnd

        Parameters
        ----------
        name : str
            Name of the interface
        node_id : str
            Id of the node that the interface belongs to
        pair : VethEnd
            The other end of this veth pair
        """

        if config.get_value("assign_random_names") is False:
            if len(name) > MAX_CUSTOM_NAME_LEN:
                raise ValueError(
                    f"Interface name {name} is too long. Interface names "
                    f"should not exceed 15 characters"
                )

        super().__init__(name, node_id)
        self._address = None
        self._pair = pair
        self.bandwidth = None
        self.delay = None

        self._mtu = 1500
        self._is_mpls_enabled = False

    @property
    def pair(self):
        """
        Get other pair for this interface (assuming veth)
        """
        return self._pair

    @pair.setter
    def pair(self, interface):
        """
        Setter for the other end of the interface that it is connected to

        Parameters
        ----------
        interface : Interface
            The interface to which this interface is connected to
        """
        self._pair = interface

    @property
    def subnet(self):
        """Getter for the subnet to which the address belongs to"""
        return self.address.get_subnet()

    @property
    def address(self):
        """
        Getter for the address associated
        with the interface
        """
        return self._address

    @address.setter
    def address(self, address):
        """
        Assigns IP address to an interface

        Parameters
        ----------
        address : Address or str
            IP address to be assigned to the interface
        """
        if isinstance(address, str):
            address = Address(address)

        if self._node_id is not None:
            engine.assign_ip(self._node_id, self.id, address.get_addr())
            self._address = address
        else:
            # TODO: Create our own error class
            raise NotImplementedError(
                "You should assign the interface to node or router before assigning address to it."
            )

        # Global variable to check if address is ipv6 or not for DAD check
        if address.is_ipv6() is True:
            g_var.IS_IPV6 = True

    def get_address(self):
        """
        Getter for the address associated
        with the interface

        *NOTE*: Maintained since mentioned in NeST paper.
        """
        return self.address

    def set_address(self, address):
        """
        Assigns IP address to an interface

        Parameters
        ----------
        address : Address or str
            IP address to be assigned to the interface

        *NOTE*: Maintained since mentioned in NeST paper.
        """
        self.address = address

    def disable_ip_dad(self):
        """
        Disables Duplicate addresses Detection (DAD) for an interface.
        """
        engine.disable_dad(self._node_id, self._id)

    def enable_mpls(self):
        """
        Enables mpls input through the interface.
        Requires mpls kernel modules to be loaded.

        Run ``sudo modprobe mpls_iptunnel`` to load mpls modules.
        """
        if self._node_id is None:
            raise NotImplementedError(
                "You should assign the interface to node or router before enabling mpls"
            )

        engine.set_mpls_max_label_node(self.node_id, int(100000))

        if self._is_mpls_enabled is False:
            engine.enable_mpls_interface(self._node_id, self.id)
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
            engine.set_mtu_interface(self._node_id, self.id, int(mtu_value))
            self._mtu = mtu_value
            logger.debug("MTU of interface %s set to %s", self.name, str(self.mtu))
