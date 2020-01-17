# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

from . import engine
from . import error_handling
from . import topology

# Filter supported types
_support = {
    'protocol': ['ip'],
    'filtertype': ['u32'],
}

class Qdisc:

    def __init__(self, dev_name, qdisc, parent = 'root', handle = '', **kwargs):
        """
        Constructor to add a qdisc (Queueing Discipline) to an interface (device)

        :param qdisc: The qdisc which needs to be added to the interface
        :type qdisc: string
        :param dev_name: The interface to which the qdisc is to be added
        :type dev_name: Interface class
        :param parent: id of the parent class in major:minor form(optional)
        :type parent: string
        :param handle: id of the filter
        :type handle: string
        :param **kwargs: qdisc specific paramters 
        :type **kwargs: dictionary
        """

        # Verify all the paramaters
        error_handling.type_verify('qdisc', qdisc, 'string', str)
        error_handling.type_verify('dev_name', dev_name, 'Interface class', topology.Interface)
        error_handling.type_verify('parent', parent, 'string', str)
        error_handling.type_verify('handle', handle, 'string', str)

        engine.add_qdisc(dev_name.ns_name, dev_name, qdisc, parent, handle, kwargs)


class Class:

    def __init__(self, dev_name, qdisc, parent = 'root', classid = '', **kwargs):
        """
        Constructor to create an object that represents a class

        :param dev_name: The interface to which the qdisc is to be added
        :type dev_name: Interface class
        :param qdisc: The qdisc which needs to be added to the interface
        :type qdisc: string
        :param parent: id of the parent class in major:minor form(optional)
        :type parent: string
        :param classid: id of the class
        :type classid: string
        :param **kwargs: class specific paramters 
        :type **kwargs: dictionary
        """

        # Verify all the parameters
        error_handling.type_verify('qdisc', qdisc, 'string', str)
        error_handling.type_verify('dev_name', dev_name, 'Interface class', topology.Interface)
        error_handling.type_verify('parent', parent, 'string', str)
        error_handling.type_verify('classid', classid, 'string', str)

        engine.add_class(dev_name.ns_name, dev_name, parent, qdisc, classid, kwargs)


class Filter:

    def __init__(self, protocol, priority, filtertype, flowid, parent='root', filter=None):
        """
        Constructor to design a Filter to assign to a Class
        or Qdisc

        :param protocol: protocol used
        :type protocol: string
        :param priority: priority of the filter
        :type priority: int
        :param filtertype: one of the available filters
        :type filtertype: string
        :param flowid: classid of the class where the traffic is enqueued 
                       if the traffic passes the filter
        :type flowid: Class
        :param parent: id of the parent class in major:minor form(optional)
        :type parent: string
        :param filter: filter parameters
        :type filter: dictionary
        """

        # Verify all parameters
        error_handling.type_verify('protocol', protocol, 'string', str, supported_parameters=['protocol'])
        error_handling.type_verify('priority', priority, 'int', int)
        error_handling.type_verify('filtertype', filtertype, 'string', str, supported_parameters=['filtertype'])

        if filter is None:
            # TODO: better error msg
            raise ValueError('filter cannot be None! Pass a dictionary of parameters')

        #TODO: Invoke engine function to setup the filter