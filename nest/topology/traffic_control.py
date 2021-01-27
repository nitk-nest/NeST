# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Handle traffic control entities"""

from .. import engine

# TODO: Improve this module such that the below pylint disables are no
# longer required

# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes


class Qdisc:
    """Handle Queueing Discipline"""

    def __init__(self, namespace_id, dev_id, qdisc, parent="root", handle="", **kwargs):
        """
        Constructor to add a qdisc (Queueing Discipline) to an interface (device)

        Parameters
        ----------
        namespace_id : str
            The id of the namespace to which the interface belongs to
        dev_id : str
            The id of the interface to which the qdisc is to be added
        qdisc : str
            The qdisc which needs to be added to the interface
        dev_id : str
            The id of the interface to which the qdisc is to be added
        namespace_id : str
            The id of the namespace that the device belongs to
        parent : str
            id of the parent class in major:minor form(optional)
        handle : str
            id of the filter
        """
        self.namespace_id = namespace_id
        self.dev_id = dev_id
        self.qdisc = qdisc
        self.parent = parent
        self.handle = handle

        engine.add_qdisc(namespace_id, dev_id, qdisc, parent, handle, **kwargs)


class Class:
    """Handle classes associated to qdisc"""

    def __init__(
        self, namespace_id, dev_id, qdisc, parent="root", classid="", **kwargs
    ):
        """
        Constructor to create an object that represents a class

        Parameters
        ----------
        namespace_id : str
            The id of the namespace to which the interface belongs to
        dev_id : str
            The id of the interface to which the qdisc is to be added
        namespace_id : str
            The id of the namespace that the device belongs to
        qdisc : str
            The qdisc which needs to be added to the interface
        parent : str
            id of the parent class in major:minor form(optional)
        classid : str
            id of the class
        """
        self.namespace_id = namespace_id
        self.dev_id = dev_id
        self.qdisc = qdisc  # NOTE: should be renamed to knid
        self.parent = parent
        self.classid = classid

        engine.add_class(namespace_id, dev_id, parent, qdisc, classid, **kwargs)


class Filter:
    """Handle filters to assign to class/qdisc"""

    def __init__(
        self,
        namespace_id,
        dev_id,
        protocol,
        priority,
        filtertype,
        flowid,
        parent="root",
        handle="",
        **kwargs
    ):
        """
        Constructor to design a Filter to assign to a Class or Qdisc

        Parameters
        ----------
        namespace_id : str
            The id of the namespace to which the interface belongs to
        dev_id : str
            The id of the interface to which the qdisc is to be added
        protocol : str
            protocol used
        priority : int
            priority of the filter
        filtertype : str
            one of the available filters
        flowid : Class
            classid of the class where the traffic is enqueued
            if the traffic passes the filter
        parent : str
            id of the parent class in major:minor form(optional)
        handle : str
            id of the filter
        filter : dictionary
            filter parameters
        """
        self.namespace_id = namespace_id
        self.dev_id = dev_id
        self.protocol = protocol
        self.priority = priority
        self.filtertype = filtertype
        self.flowid = flowid
        self.parent = parent
        self.handle = handle

        engine.add_filter(
            namespace_id,
            dev_id,
            protocol,
            priority,
            filtertype,
            parent,
            handle,
            **kwargs
        )
