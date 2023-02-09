# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""API related to device creation in topology"""

import logging
from nest import config
from nest.topology_map import TopologyMap
from nest.topology.id_generator import IdGen
from nest.topology.device.traffic_control import TrafficControlHandler
from nest import engine
import nest.global_variables as g_var
from nest.exception import NestBaseException
from nest.topology.address import Address

logger = logging.getLogger(__name__)

# Max length of device when Topology Map is disabled
# i.e. 'assign_random_names' is set to False in config
MAX_CUSTOM_NAME_LEN = 15

# pylint: disable=too-many-public-methods
# pylint: disable=too-many-instance-attributes


class Device:
    """
    A common subclass which all devices inherit

    Attributes
    ----------

    name : str
        User given name for the device
    id : str
        This value is used by `engine` to create emulated device
        entity
    node_id : str
        This is id of the node that the device belongs to
    traffic_ctl_hanlder : TrafficControlHanlder
        Takes care of traffic control for the device
    """

    def __init__(self, name, node_id):
        """
        Constructore for a device

        Parameters
        ----------
        name : str
            User given name for the device
        node_id : str
            This is the id of the node that the device belongs to
        """

        if config.get_value("assign_random_names") is False:
            if len(name) > MAX_CUSTOM_NAME_LEN:
                raise ValueError(
                    f"Device name {name} is too long. Device names "
                    f"should not exceed 15 characters"
                )
        self._ipv4_address = []
        self._ipv6_address = []
        self._name = name
        self._id = IdGen.get_id(name)
        self._traffic_control_handler = TrafficControlHandler(node_id, self._id)
        if node_id is not None:
            TopologyMap.add_device(self.node_id, self.id, self)

        self._set_structure = False
        self._mtu = 1500
        self._is_mpls_enabled = False

    @property
    def name(self):
        """Getter for name"""
        return self._name

    @property
    def id(self):
        """Getter for id"""
        return self._id

    @property
    def qdisc_list(self):
        """
        Getther for the list of all qdiscs
        """
        return self._traffic_control_handler.qdisc_list

    @property
    def node_id(self):
        """
        Getter for the `Node` associated
        with the device
        """
        return self._traffic_control_handler.node_id

    @node_id.setter
    def node_id(self, node_id):
        """
        Setter for the `Node` associated
        with the device

        Parameters
        ----------
        node : str
            The id of the node where the device is to be installed
        """
        self._traffic_control_handler.node_id = node_id
        if node_id is not None:
            TopologyMap.add_device(self.node_id, self.id, self)

    def set_mode(self, mode):
        """
        Changes the mode of the device

        Parameters
        ----------
        mode : string
            device mode to be set
        """
        if mode in ("UP", "DOWN"):
            if self.node_id is not None:
                engine.set_interface_mode(self.node_id, self.id, mode.lower())
            else:
                # TODO: Create our own error class
                raise NotImplementedError(
                    "You should assign the device to node or router before setting it's mode"
                )
        else:
            raise ValueError(
                f'{mode} is not a valid mode (it has to be either "UP" or "DOWN")'
            )

    def _validate_transform_address(self, func_name, address):
        """
        Internal method to validate Address/str or List[Address/str] input type
        and transform it into List[Address]

        Parameters
        ----------
        func_name : str
            Name of the function that is using this validation
        address : Address/str or List[Address/str]
            IP address(es) to be validated and transformed
        """

        init_type = type(address)
        if isinstance(address, str):
            address = [Address(address)]
        elif isinstance(address, list):
            for i in range(len(address)):
                if isinstance(address[i], str):
                    address[i] = Address(address[i])
                elif not isinstance(address[i], Address):
                    raise TypeError(
                        f"Expected type of argument 'address' in method '{func_name}'"
                        " is Address/str or List[Address/str]. "
                        f"But got input '{address}' of type List[{type(address[i])}]"
                    )
        elif isinstance(address, Address):
            address = [address]
        else:
            raise TypeError(
                f"Expected type of argument 'address' in method '{func_name}'"
                " is Address/str or List[Address/str]. "
                f"But got input '{address}' of type {init_type}"
            )

        if self.node_id is None:
            raise DeviceNotPartOfNodeError(
                "You should assign the interface to node or router before assigning address to it."
            )

        return address

    def set_address(self, address):
        """
        Assigns IP address/addresses to an interface

        Parameters
        ----------
        address : Address/str or List[Address/str]
            IP address to be assigned to the interface
        """

        # Make arguments to a list of Address objects and validate type
        address = self._validate_transform_address("set_address", address)

        # Deleting old ip addresses
        for addr in self._ipv4_address:
            engine.delete_ip(self.node_id, self.id, addr.get_addr())
        self._ipv4_address = []
        for addr in self._ipv6_address:
            engine.delete_ip(self.node_id, self.id, addr.get_addr())
        self._ipv6_address = []

        # Adding new ip addresses
        for addr in address:
            engine.assign_ip(self.node_id, self.id, addr.get_addr())
            if addr.is_ipv6() is True:
                self._ipv6_address.append(addr)
            else:
                self._ipv4_address.append(addr)

        # Global variable to check if address is ipv6 or not for DAD check
        if len(self._ipv6_address) != 0:
            g_var.IS_IPV6 = True

    def add_address(self, address):
        """
        Adds IP address to an interface

        Parameters
        ----------
        address : Address/str or List[Address/str]
            IP address to be added to the interface
        """

        # Make arguments to a list of Address objects and validate type
        address = self._validate_transform_address("add_address", address)

        for addr in address:
            engine.assign_ip(self.node_id, self.id, addr.get_addr())
            if addr.is_ipv6() is True:
                self._ipv6_address.append(addr)
            else:
                self._ipv4_address.append(addr)

    def get_address(self, ipv4=True, ipv6=True, as_list=False):
        """
        Gets the required IP addresses for the interface
        Returns a list or an Address object
        Parameters
        ----------
        ipv4 : If set to true, the IPv4 address of the interface is returned (defaults to True)
        ipv6 : If set to true, the IPv6 address of the interface is returned (defaults to True)
        If both are True, both the addresses are returned
        Either ipv4 or ipv6 must be True
        as_list : Only applicable when a single address is set (Applicable individually for
                  ipv4 and ipv6).
        Returns Address object when false, else returns a single Address object in list
        (defaults to False).
        """

        # check if one of ipv4/ipv6 is true
        if not (ipv4 or ipv6):
            raise ValueError("Either ipv4 or ipv6 argument must be True")

        list_of_addresses = []

        if ipv4:
            list_of_addresses += self._ipv4_address
        if ipv6:
            list_of_addresses += self._ipv6_address

        if len(list_of_addresses) == 1 and as_list is False:
            return list_of_addresses[0]

        return list_of_addresses

    def del_address(self, address):
        """
        Delete IP address(es) from the interface

        Parameters
        ----------
        address : str or list
            IP address to be deleted from the interface
        """
        # Make arguments to a list of Address objects and validate type
        address = self._validate_transform_address("del_address", address)

        for addr in address:
            deleted = None
            if addr.is_ipv6():
                for i in range(len(self._ipv6_address)):
                    if self._ipv6_address[i].get_addr() == addr.get_addr():
                        engine.delete_ip(self.node_id, self.id, addr.get_addr())
                        deleted = self._ipv6_address.pop(i)
                        break
            else:
                for i in range(len(self._ipv4_address)):
                    if self._ipv4_address[i].get_addr() == addr.get_addr():
                        engine.delete_ip(self.node_id, self.id, addr.get_addr())
                        deleted = self._ipv4_address.pop(i)
                        break
            if deleted is None:
                addrs = addr.get_addr()
                logger.warning(
                    "Cannot delete an address that is not assigned. (%s)", addrs
                )

    def add_qdisc(self, qdisc, parent="root", handle="", **kwargs):
        """
        Add a qdisc (Queueing Discipline) to this device

        Parameters
        ----------
        qdisc : string
            The qdisc which needs to be added to the device
        dev : Interface class
            The device to which the qdisc is to be added
        parent : string
            id of the parent class in major:minor form(optional) (Default value = 'root')
        handle : string
            id of the filter (Default value = '')
        """

        self._traffic_control_handler.add_qdisc(qdisc, parent, handle, **kwargs)

    def change_qdisc(self, handle, qdisc="", **kwargs):
        """
        Change a qdisc that is already present in the device

        Parameters
        ----------
        handle : string
            Hande of the qdisc to be changed
        qdisc : string
            The new qdisc to be added to the device
        """

        self._traffic_control_handler.change_qdisc(handle, qdisc, **kwargs)

    def delete_qdisc(self, handle):
        """
        Delete qdisc (Queueing Discipline) from this device

        Parameters
        ----------
        handle : string
            Handle of the qdisc to be deleted
        """

        self._traffic_control_handler.delete_qdisc(handle)

    def add_class(self, qdisc, parent="root", classid="", **kwargs):
        """
        Create an object that represents a class

        Parameters
        ----------
        qdisc : string
            The qdisc which needs to be added to the device
        parent : string
            id of the parent class in major:minor form(optional) (Default value = 'root')
        classid : string
            id of the class (Default value = '')
        """

        self._traffic_control_handler.add_class(qdisc, parent, classid, **kwargs)

    def change_class(self, qdisc, parent, classid, **kwargs):
        """
        Change a class that is already present in the device

        Parameters
        ----------
        qdisc : string
            The qdisc which needs to be added to the device
        parent : string
            id of the parent class in major:minor form(optional) (Default value = 'root')
        classid : string
            id of the class (Default value = '')
        """

        self._traffic_control_handler.change_class(qdisc, parent, classid, **kwargs)

    def delete_class(self, classid, parent):
        """
        Delete Class from this device

        Parameters
        ----------
        handle : string
            Handle of the class to be deleted
        """
        self._traffic_control_handler.delete_class(classid, parent)

    # pylint: disable=too-many-arguments
    def add_filter(
        self,
        dev_id,
        priority,
        filtertype,
        flowid,
        protocol="ip",
        parent="root",
        handle="",
        **kwargs,
    ):
        """
        Design a Filter to assign to a Class or Qdisc

        Parameters
        ----------
        dev_id : string
            Device from the packets are being mirrored
        protocol : string
            protocol used (Default value = 'ip')
        priority : int
            priority of the filter
        filtertype : string
            one of the available filters
        flowid : Class
            classid of the class where the traffic is enqueued
            if the traffic passes the filter
        parent : string
            id of the parent class in major:minor form(optional) (Default value = 'root')
        handle : string
            id of the filter (Default value = '')
        filter : dictionary
            filter parameters
        """
        # TODO: Verify type of parameters
        # TODO: Reduce arguments to the engine functions by finding parent and handle automatically

        self._traffic_control_handler.add_filter(
            dev_id, priority, filtertype, flowid, protocol, parent, handle, **kwargs
        )

    def delete_filter(self, handle, parent):
        """
        Delete filter from a Class or a Qdisc

        Parameters
        ----------
        handle : string
            Handle of the class to be deleted
        """

        self._traffic_control_handler.delete_filter(handle, parent)

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

    def __repr__(self):
        classname = self.__class__.__name__
        return f"{classname}({self.name!r})"


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


class DeviceNotPartOfNodeError(NestBaseException):
    """
    Exception related to error in not assigning Device to Node.
    """
