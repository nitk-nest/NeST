# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

from . import engine

# Filter supported types
_support = {
    'protocol': ['ip'],
    'filtertype': ['u32'],
}

class Filter:

    def __init__(self, protocol, priority, filtertype, flowid,
                parent=None, filter=None):
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
        

        def _verify_helper(self, parameter_name, parameter, type_name, 
                    expected_type, supported_parameters = None):
        """
        Helper to verify parameters passed to the constructor

        :param parameter_name: Name of the parameter being verified
        :type parameter_name: string
        :param parameter: parameter to be verified
        :param type_name: Name of the type in string
        :type type_name: string
        :param expected_type: expected type of the parameter
        :param supported_parameters: set of supported parameters
        :type supported_parameters: list{string}
        """

        if type(parameter) is not expected_type:
            raise ValueError('{} expects type {}'.format(parameter_name, type_name))
        
        if supported_parameters is not None and 
            parameter not in supported_parameters:
            raise ValueError('{} is not a supported {}'.format(parameter, parameter_name))
