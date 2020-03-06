# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

from .. import engine
from . import error_handling

# Filter supported types
_support = {
    'protocol': ['ip'],
    'filtertype': ['u32'],
}

class Qdisc:

    def __init__(self, namespace_id , dev_id, qdisc, parent = 'root', handle = '', **kwargs):
        """
        Constructor to add a qdisc (Queueing Discipline) to an interface (device)

        :param namespace_id: The id of the namespace to which the interface belongs to
        :type namespace_id: String
        :param dev_id: The id of the interface to which the qdisc is to be added
        :type dev_id: String
        :param qdisc: The qdisc which needs to be added to the interface
        :type qdisc: string
        :param dev_id: The id of the interface to which the qdisc is to be added
        :type dev_id: String
        :param namespace_id: The id of the namespace that the device belongs to
        :type namespace_id: String
        :param parent: id of the parent class in major:minor form(optional)
        :type parent: string
        :param handle: id of the filter
        :type handle: string
        :param **kwargs: qdisc specific paramters 
        :type **kwargs: dictionary
        """

        self.namespace_id = namespace_id
        self.dev_id = dev_id
        self.qdisc = qdisc
        self.parent = parent
        self.handle = handle

        # Verify all the paramaters

        error_handling.type_verify('namespace_id', namespace_id, 'string', str)
        error_handling.type_verify('dev_id', dev_id, 'string', str)
        error_handling.type_verify('qdisc', qdisc, 'string', str)
        error_handling.type_verify('namespace_id', namespace_id, 'Interface class', str)
        error_handling.type_verify('parent', parent, 'string', str)
        error_handling.type_verify('handle', handle, 'string', str)

        engine.add_qdisc(namespace_id, dev_id, qdisc, parent, handle, **kwargs)


class Class:

    def __init__(self, namespace_id , dev_id, qdisc, parent = 'root', classid = '', **kwargs):
        """
        Constructor to create an object that represents a class

        :param namespace_id: The id of the namespace to which the interface belongs to
        :type namespace_id: String
        :param dev_id: The id of the interface to which the qdisc is to be added
        :type dev_id: String
        :param namespace_id: The id of the namespace that the device belongs to
        :type namespace_id: String
        :param qdisc: The qdisc which needs to be added to the interface
        :type qdisc: string
        :param parent: id of the parent class in major:minor form(optional)
        :type parent: string
        :param classid: id of the class
        :type classid: string
        :param **kwargs: class specific paramters 
        :type **kwargs: dictionary
        """

        self.namespace_id = namespace_id
        self.dev_id = dev_id
        self.qdisc = qdisc
        self.parent = parent
        self.classid = classid

        # Verify all the parameters

        error_handling.type_verify('namespace_id', namespace_id, 'string', str)
        error_handling.type_verify('dev_id', dev_id, 'string', str)
        error_handling.type_verify('qdisc', qdisc, 'string', str)
        error_handling.type_verify('namespace_id', namespace_id, 'Interface class', str)
        error_handling.type_verify('parent', parent, 'string', str)
        error_handling.type_verify('classid', classid, 'string', str)

        engine.add_class(namespace_id, dev_id, parent, qdisc, classid, **kwargs)


class Filter:

    def __init__(self, namespace_id , dev_id, protocol, priority, filtertype, flowid, parent='root', handle = '',  **kwargs):
        """
        Constructor to design a Filter to assign to a Class
        or Qdisc

        :param namespace_id: The id of the namespace to which the interface belongs to
        :type namespace_id: String
        :param dev_id: The id of the interface to which the qdisc is to be added
        :type dev_id: String
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
        :param handle: id of the filter
        :type handle: string
        :param filter: filter parameters
        :type filter: dictionary
        :param **kwargs: filter specific paramters 
        :type **kwargs: dictionary
        """

        self.namespace_id = namespace_id
        self.dev_id = dev_id
        self.protocol = protocol
        self.priority = priority
        self.filtertype = filtertype
        self.flowid = flowid
        self.parent = parent
        self.handle = handle

        # Verify all parameters

        error_handling.type_verify('namespace_id', namespace_id, 'string', str)
        error_handling.type_verify('dev_id', dev_id, 'string', str)
        error_handling.type_verify('protocol', protocol, 'string', str, supported_parameters=['protocol'])
        error_handling.type_verify('priority', priority, 'int', int)
        error_handling.type_verify('filtertype', filtertype, 'string', str, supported_parameters=['filtertype'])
        error_handling.type_verify('flowid', flowid, 'Class', Class)
        error_handling.type_verify('parent', parent, 'string', str)
        error_handling.type_verify('handle', handle, 'string', str)

        engine.add_filter(namespace_id, dev_id, protocol, priority, filtertype, flowid, parent, handle, **kwargs)