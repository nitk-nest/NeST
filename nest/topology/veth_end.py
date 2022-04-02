# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""API related to creation of virtual ethernet devices in topology"""

import logging
from nest import config
from nest import engine
from .device import Device

logger = logging.getLogger(__name__)

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

        self.bandwidth = None
        self.delay = None
        self._set_structure = False

        self._mtu = 1500
        self._is_mpls_enabled = False

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
