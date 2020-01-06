# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

from . import engine
from . import errors
from . import topology

# Filter supported types
_support = {
    'protocol': ['ip'],
    'filtertype': ['u32'],
}

class Filter:

    def __init__(self, protocol, priority, filtertype, flowid, parent=None, filter=None):
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
        _verify_helper('protocol', protocol, 'string', str, support['protocol'])
        _verify_helper('priority', priority, 'int', int)
        _verify_helper('filtertype', filtertype, 'string', str, support['filtertype'])

        # If parant is None, assume root
        if parant in None:
            parent = 'root'

        if filter is None:
            # TODO: better error msg
            raise ValueError('filter cannot be None! Pass a dictionary of parameters')

        #TODO: Invoke engine function to setup the filter


class Qdisc:

    def __init__(self, qdisc, interface, parent = None, handle = None, **kwargs)
        """
        Constructor to add a qdisc (Queueing Discipline) to an interface (device)

        :param qdisc: The qdisc which needs to be added to the interface
        :type qdisc: string
        :param interface: The interface to which the qdisc is to be added
        :type interface: Interface class
        :param parent: id of the parent class in major:minor form(optional)
        :type parent: string
        :param handle: id of the filter
        :type handle: string
        :param **kwargs: qdisc specific paramters 
        :type **kwargs: dictionary
        """

        # Verify all the paramaters
        _verify_helper('qdisc', qdisc, 'string', str)
        _verify_helper('interface', interface, 'Interface class', Interface)
        
        