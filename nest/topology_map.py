# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""
NeST internally uses auto-generated unique ids to name topologies.
This module holds the mapping between the user given names and the names
generated internally by NeST.
"""

import json
import logging

logger = logging.getLogger(__name__)


class TopologyMap:
    """
    Store mapping between user given names and NeST ids
    """

    # topology_map contains the information about topology created
    topology_map = {"namespaces": [], "hosts": [], "routers": []}
    # NOTE:
    # To figure out the contents of each dict keyword,
    # checkout the add_keyword function.
    # For example, to get the contents of qdisc parameter,
    # checkout add_qdisc function

    # Pointer to topology_map['namespaces']
    # Used for efficiency
    # orphan interfaces are those interfaces which do not belong to any network
    # list of network is used to store all the existing network object
    namespaces_pointer = {}
    list_of_network = []
    orphan_interfaces = 0

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
            raise ValueError(f"Namespace with id {ns_id} already exists in TopologyMap")

        namespaces = TopologyMap.get_namespaces()

        namespaces.append({"id": ns_id, "name": ns_name, "interfaces": []})

        TopologyMap.namespaces_pointer[ns_id] = {
            "pos": len(namespaces) - 1,
            "interfaces_pointer": {},
        }

    @staticmethod
    def add_host(host):
        """
        Add host to topology_map. This is required apart
        from `add_namespaces` for routing

        Parameters
        ----------
        ns_id : str
            namepspace id of the host
        ns_name : str
            namespace name of the host
        """
        hosts = TopologyMap.get_hosts()

        hosts.append(host)

    @staticmethod
    def add_router(router):
        """
        Add router to topology_map. This is required apart
        from `add_namespaces` for routing

        Parameters
        ----------
        ns_id : str
            namepspace id of the router
        ns_name : str
            namespace name of the router
        """
        routers = TopologyMap.get_routers()

        routers.append(router)
        TopologyMap.get_hosts().remove(router)  # remove the router from hosts list

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
            raise ValueError(f"Namespace with id {ns_id} doesn't exist in TopologyMap")

        if int_id in TopologyMap.namespaces_pointer[ns_id]["interfaces_pointer"]:
            raise ValueError(
                f"Interface with id {int_id} already present in namespace {ns_id}"
            )

        # TODO: classes not added yet to list
        interfaces = TopologyMap.get_interfaces(ns_id)

        interfaces.append({"id": int_id, "name": int_name, "qdiscs": []})

        TopologyMap.orphan_interfaces = TopologyMap.orphan_interfaces + 1

        TopologyMap.namespaces_pointer[ns_id]["interfaces_pointer"][int_id] = {
            "pos": len(interfaces) - 1
        }

    @staticmethod
    def add_qdisc(ns_id, int_id, kind, handle, parent=""):
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
            raise ValueError(f"Namespace with id {ns_id} doesn't exist in TopologyMap")

        if int_id not in TopologyMap.namespaces_pointer[ns_id]["interfaces_pointer"]:
            raise ValueError(
                f"Interface with id {int_id} doesn't exist in namespace {ns_id}"
            )

        # TODO: Check if qdisc is already present?

        qdiscs = TopologyMap.get_qdiscs(ns_id, int_id)
        qdiscs.append({"kind": kind, "handle": handle, "parent": parent})

    @staticmethod
    def change_qdisc(ns_id, int_id, kind, handle):
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
            raise ValueError(f"Namespace with id {ns_id} doesn't exist in TopologyMap")

        if int_id not in TopologyMap.namespaces_pointer[ns_id]["interfaces_pointer"]:
            raise ValueError(
                f"Interface with id {int_id} doesn't exist in namespace {ns_id}"
            )

        qdiscs = TopologyMap.get_qdiscs(ns_id, int_id)
        for qdisc in qdiscs:
            if qdisc["handle"] == handle:
                qdisc["kind"] = kind

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
            if qdisc["handle"] == handle:
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
        return TopologyMap.topology_map["namespaces"]

    @staticmethod
    def get_routers():
        """
        Get all routers added

        Returns
        -------
        List[Dict]
        """
        return TopologyMap.topology_map["routers"]

    @staticmethod
    def get_hosts():
        """
        Get all hosts added

        Returns
        -------
        List[Dict]
        """
        return TopologyMap.topology_map["hosts"]

    @staticmethod
    def get_namespace(ns_id, with_interfaces_pointer=False):
        """
        Get namespace given its id

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
        namespace = namespaces[namespace_pointer["pos"]]

        if with_interfaces_pointer:
            return (namespace_pointer["interfaces_pointer"], namespace)

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
        interfaces = namespace["interfaces"]

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
        (interfaces_pointer, _) = TopologyMap.get_namespace(
            ns_id, with_interfaces_pointer=True
        )
        interfaces = TopologyMap.get_interfaces(ns_id)
        interface_pointer = interfaces_pointer[int_id]
        interface = interfaces[interface_pointer["pos"]]

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
        qdiscs = interface["qdiscs"]

        return qdiscs

    @staticmethod
    def delete_all_mapping():
        """
        Delete all mappings stored in `TopologyMap`.
        """
        TopologyMap.topology_map = {"namespaces": [], "hosts": [], "routers": []}
        TopologyMap.namespaces_pointer = {}
        TopologyMap.list_of_network = []
        TopologyMap.orphan_interfaces = 0

    @staticmethod
    def dump():
        """
        Dump generated topology_map. (for debugging purposes)
        """
        logger.debug("Config")
        logger.debug("------")
        logger.debug(json.dumps(TopologyMap.topology_map, indent=4))

        # print()
        # print('Pointers')
        # print('--------')
        # print(json.dumps(TopologyMap.namespaces_pointer, indent = 4))

    @staticmethod
    def add_network(network):
        """
        Add network object reference to topology_map

        Parameters
        ----------
        network : Network
            Object reference of Network class
        """
        TopologyMap.list_of_network.append(network)

    @staticmethod
    def decrement_orphan_interfaces():
        """
        Reduce the orphan interface in the topology

        """
        TopologyMap.orphan_interfaces = TopologyMap.orphan_interfaces - 1
