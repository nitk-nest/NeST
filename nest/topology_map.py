# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# nest internally uses auto-generated unique id's to name
# topologies.
# This module holds the mapping between user given names and
# nest's names.

import atexit
from . import engine

class TopologyMap():

    # topology_map contains the info about topology created
    topology_map = {
        'namespaces': [],
    }
    # NOTE:
    # To figure out the contents of each dict keyword,
    # checkout the add_keyword function.
    # For eg, to get the contents of qdisc parameter,
    # checkout add_qdisc function

    # Pointer to topology_map['namespaces']
    # Used for efficiency
    namespaces_pointer = {}

    def __init__():
        pass

    @staticmethod
    def add_namespace(id, ns_name):
        """
        Add namespace to topology_map

        :param id: namepspace id
        :type id: string
        :param ns_name: namespace name
        :type ns_name: string
        """

        namespaces = TopologyMap.get_namespaces()

        namespaces.append({
            'id': id,
            'name': ns_name,
            'interfaces': []
        })

        TopologyMap.namespaces_pointer[id] = {
            'pos': len(namespaces)-1,
            'interfaces_pointer': {}
        }

    @staticmethod
    def add_interface(ns_id, id, int_name):
        """
        Add interface to topology_map

        :param ns_id: namepspace id
        :type ns_id: string
        :param id: interface id
        :type id: string
        :param int_name: interface name
        :type id: string
        """

        # TODO: classes not added yet to list
        interfaces = TopologyMap.get_interfaces(ns_id)

        interfaces.append({
            'id': id,
            'name': int_name,
            'qdiscs': []
        })

        TopologyMap.namespaces_pointer[ns_id]['interfaces_pointer'][id] = {
            'pos': len(interfaces)-1
        }

    @staticmethod
    def add_qdisc(ns_id, int_id, kind, handle, parent=''):
        """
        Add qdisc to topology_map

        :param ns_id: namepspace id
        :type ns_id: string
        :param int_id: interface id
        :type int_id: string
        :param kind: qdisc kind
        :type kind: string
        :param handle: qdisc handle
        :type handle: string
        :param parent: qdisc parent
        :type parent: string
        """

        qdiscs = TopologyMap.get_qdiscs(ns_id, int_id)
        qdiscs.append({
            'kind': kind,
            'handle': handle,
            'parent': parent
        })

    @staticmethod
    def delete_qdisc(ns_id, int_id, handle):
        """
        Delete qdisc from topology_map

        :param ns_id: namepspace id
        :type ns_id: string
        :param int_id: interface id
        :type int_id: string
        :param handle: qdisc handle
        :type handle: string
        """

        qdiscs = TopologyMap.get_qdiscs(ns_id, int_id)
        counter = 0
        for qdisc in qdiscs:
            if qdisc['handle'] == handle:
                qdiscs.pop(counter)
                break
            counter += 1

    @staticmethod
    def get_topology_map():
        return TopologyMap.topology_map

    @staticmethod
    def get_namespaces():
        return TopologyMap.topology_map['namespaces']

    @staticmethod
    def get_namespace(ns_id, with_interfaces_pointer=False):
        """
        Get namespace given it's id

        :param ns_id: namespace id
        :type ns_id: string
        :param with_interfaces_pointer: If should return interfaces_pointer for the namespace
        :type with_interfaces_pointer: bool
        """

        namespaces = TopologyMap.get_namespaces()
        namespace_pointer = TopologyMap.namespaces_pointer[ns_id]
        namespace = namespaces[namespace_pointer['pos']]

        if with_interfaces_pointer:
            return (namespace_pointer['interfaces_pointer'], namespace)
        else:
            return namespace

    @staticmethod
    def get_interfaces(ns_id):
        """
        Get all interfaces in the namespace

        :param ns_id: namespace id
        :type ns_id: string
        """

        namespace = TopologyMap.get_namespace(ns_id)
        interfaces = namespace['interfaces']

        return interfaces

    @staticmethod
    def get_interface(ns_id, int_id):
        """
        Get interface in namespace `ns_id` with interface
        `int_id`

        :param ns_id: namespace id
        :type ns_id: string
        :param int_id: interface id
        :type int_id: string
        """

        (interfaces_pointer, namespace) = TopologyMap.get_namespace(
            ns_id, with_interfaces_pointer=True)
        interfaces = TopologyMap.get_interfaces(ns_id)
        interface_pointer = interfaces_pointer[int_id]
        interface = interfaces[interface_pointer['pos']]

        return interface

    @staticmethod
    def get_qdiscs(ns_id, int_id):
        """
        Get qdiscs in namespace `ns_id` with interface
        `int_id`

        :param ns_id: namespace id
        :type ns_id: string
        :param int_id: interface id
        :type int_id: string
        """

        interface = TopologyMap.get_interface(ns_id, int_id)
        qdiscs = interface['qdiscs']

        return qdiscs

    def dump():
        """
        Dump generated topology_map. (for debugging purposes)
        """

        import json

        print('Config')
        print('------')
        print(json.dumps(TopologyMap.topology_map, indent=4))

        # print()
        # print('Pointers')
        # print('--------')
        # print(json.dumps(TopologyMap.namespaces_pointer, indent = 4))

    @atexit.register
    def delete_namespaces():
        """
        Delete all the newly generated namespaces
        """
        
        namespaces = TopologyMap.get_namespaces()
        
        for namepspace in namespaces:
            engine.delete_ns(namepspace['id'])

        print('Cleaned up environment')
