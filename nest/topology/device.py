# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""API related to device creation in topology"""

import logging
import nest.config as config
from nest.topology_map import TopologyMap
from nest.topology.id_generator import IdGen
from nest.topology.traffic_control import TrafficControlHandler
from nest import engine

logger = logging.getLogger(__name__)

# Max length of device when Topology Map is disabled
# i.e. 'assign_random_names' is set to False in config
MAX_CUSTOM_NAME_LEN = 15


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

        self._name = name
        self._id = IdGen.get_id(name)
        self._traffic_control_handler = TrafficControlHandler(node_id, self._id)
        if node_id is not None:
            TopologyMap.add_interface(self.node_id, self._id, self._name)

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
            TopologyMap.add_interface(self.node_id, self._id, self._name)

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
            priority, filtertype, flowid, protocol, parent, handle, **kwargs
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

    def __repr__(self):
        classname = self.__class__.__name__
        return f"{classname}({self.name!r})"
