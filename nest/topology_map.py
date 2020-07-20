# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""
NeST internally uses auto-generated unique id's to name topologies.
This module holds the mapping between user given names and
nest's names.
"""

import atexit
import json
from . import engine

class TopologyMap():
    """
    Store mapping between user given names and NeST's ids
    """

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

    @staticmethod
    def add_namespace(ns_id, ns_name):
        """
        Add namespace to topology_map

        Parameters
        ----------
        ns_id : str
            namepspace id
        ns_name : str
            namespace name
        """
        if ns_id in TopologyMap.namespaces_pointer:
            raise ValueError(f'Namespace with id {ns_id} already exists in TopologyMap')

        namespaces = TopologyMap.get_namespaces()

        namespaces.append({
            'id': ns_id,
            'name': ns_name,
            'interfaces': []
        })

        TopologyMap.namespaces_pointer[ns_id] = {
            'pos': len(namespaces)-1,
            'interfaces_pointer': {}
        }

    @staticmethod
    def add_interface(ns_id, int_id, int_name):
        """
        Add interface to topology_map

        Parameters
        ----------
        ns_id : str
            namepspace id
        int_id : str
            interface id
        int_name :
            interface name
        """
        if ns_id not in TopologyMap.namespaces_pointer:
            raise ValueError(f'Namespace with id {ns_id} doesn\'t exist in TopologyMap')

        if int_id in TopologyMap.namespaces_pointer[ns_id]['interfaces_pointer']:
            raise ValueError(f'Interface with id {int_id} already present in namespace {ns_id}')

        # TODO: classes not added yet to list
        interfaces = TopologyMap.get_interfaces(ns_id)

        interfaces.append({
            'id': int_id,
            'name': int_name,
            'qdiscs': []
        })

        TopologyMap.namespaces_pointer[ns_id]['interfaces_pointer'][int_id] = {
            'pos': len(interfaces)-1
        }

    @staticmethod
    def add_qdisc(ns_id, int_id, kind, handle, parent=''):
        """
        Add qdisc to topology_map

        Parameters
        ----------
        ns_id : str
            namepspace id
        int_id : str
            interface id
        kind : str
            qdisc kind
        handle : str
            qdisc handle
        parent : str
            qdisc parent (Default value = '')
        """
        if ns_id not in TopologyMap.namespaces_pointer:
            raise ValueError(f'Namespace with id {ns_id} doesn\'t exist in TopologyMap')

        if int_id not in TopologyMap.namespaces_pointer[ns_id]['interfaces_pointer']:
            raise ValueError(f'Interface with id {int_id} doesn\'t exist in namespace {ns_id}')

        # TODO: Check if qdisc is already present?

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

        Parameters
        ----------
        ns_id : str
            namepspace id
        int_id : str
            interface id
        handle : str
            qdisc handle
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
        """Get the entire topology map"""
        return TopologyMap.topology_map

    @staticmethod
    def get_namespaces():
        """
        Get all namespaces added

        Returns
        -------
        List[Dict]
        """
        return TopologyMap.topology_map['namespaces']

    @staticmethod
    def get_namespace(ns_id, with_interfaces_pointer=False):
        """
        Get namespace given it's id

        Parameters
        ----------
        ns_id : str
            namespace id
        with_interfaces_pointer : bool
            If should return interfaces_pointer for the namespace (Default value = False)

        Returns
        -------
        Dict
            Required namespace with id, name and interfaces in it
        """
        namespaces = TopologyMap.get_namespaces()
        namespace_pointer = TopologyMap.namespaces_pointer[ns_id]
        namespace = namespaces[namespace_pointer['pos']]

        if with_interfaces_pointer:
            return (namespace_pointer['interfaces_pointer'], namespace)

        return namespace

    @staticmethod
    def get_interfaces(ns_id):
        """
        Get all interfaces in the namespace

        Parameters
        ----------
        ns_id : str
            namespace id

        Returns
        -------
            List[Dict]
        """
        namespace = TopologyMap.get_namespace(ns_id)
        interfaces = namespace['interfaces']

        return interfaces

    @staticmethod
    def get_interface(ns_id, int_id):
        """
        Get interface in namespace `ns_id` with interface
        `int_id`

        Parameters
        ----------
        ns_id : str
            namespace id
        int_id : str
            interface id

        Returns
        -------
        Dict
            Interface details
        """
        (interfaces_pointer, _) = TopologyMap.get_namespace(ns_id, with_interfaces_pointer=True)
        interfaces = TopologyMap.get_interfaces(ns_id)
        interface_pointer = interfaces_pointer[int_id]
        interface = interfaces[interface_pointer['pos']]

        return interface

    @staticmethod
    def get_qdiscs(ns_id, int_id):
        """
        Get qdiscs in namespace `ns_id` with interface
        `int_id`

        Parameters
        ----------
        ns_id : str
            namespace id
        int_id : str
            interface id

        Returns
        -------
            List[Dict]
        """
        interface = TopologyMap.get_interface(ns_id, int_id)
        qdiscs = interface['qdiscs']

        return qdiscs

    @staticmethod
    def delete_all_mapping():
        """
        Delete all mappings stored in `TopologyMap`.
        """
        TopologyMap.topology_map = {
            'namespaces': [],
        }
        TopologyMap.namespaces_pointer = {}

    @staticmethod
    def dump():
        """
        Dump generated topology_map. (for debugging purposes)
        """
        print('Config')
        print('------')
        print(json.dumps(TopologyMap.topology_map, indent=4))

        # print()
        # print('Pointers')
        # print('--------')
        # print(json.dumps(TopologyMap.namespaces_pointer, indent = 4))

    @staticmethod
    @atexit.register
    def delete_namespaces():
        """
        Delete all the newly generated namespaces
        """
        namespaces = TopologyMap.get_namespaces()

        for namepspace in namespaces:
            engine.delete_ns(namepspace['id'])

        print('Cleaned up environment')
