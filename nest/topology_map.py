# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""
NeST internally uses auto-generated unique ids to name topologies.
This module holds the mapping between the user given names and the names
generated internally by NeST.
"""

import json
import logging
from threading import RLock

logger = logging.getLogger(__name__)

DEFAULT_NAMESPACE_ID = "default-namespace-0"

# pylint: disable-msg=R0904


class TopologyMap:
    """
    Store mapping between user given names and NeST ids
    """

    # NOTE:
    # Specifing None in the APIs inplace of ns_id will consider
    # it as adding, deleting or moving device from
    # default namespace, as the API's are compatible to accept None
    # as default namespace

    nodes = {}
    devices = {DEFAULT_NAMESPACE_ID: {}}
    hosts = []
    routers = []
    networks = []
    orphan_interfaces = 0
    lock = RLock()

    @staticmethod
    def add_node(ns_id, node):
        """
        Add node to TopologyMap

        Parameters
        ----------
        ns_id : str
            namespace id
        node : Node
            Object reference of Node class
        """
        # Acquire lock before entering
        with TopologyMap.lock:
            nodes = TopologyMap.get_nodes()

            if ns_id in nodes:
                raise ValueError(f"Node with {ns_id} already exists in the TopologyMap")

            nodes[ns_id] = node
            TopologyMap.devices[ns_id] = {}

    @staticmethod
    def add_host(host):
        """
        Add host to topology_map. This is required apart
        from `add_node` for routing

        Parameters
        ----------
        host : Node
            Object reference of Node class
        """
        with TopologyMap.lock:
            hosts = TopologyMap.get_hosts()

            hosts.append(host)

    @staticmethod
    def add_router(router):
        """
        Add router to topology_map. This is required apart
        from `add_node` for routing

        Parameters
        ----------
        router : Router
            Object reference of Router class
        """
        with TopologyMap.lock:
            routers = TopologyMap.get_routers()
            if router not in routers:
                routers.append(router)
                TopologyMap.get_hosts().remove(
                    router
                )  # remove the router from hosts list

    @staticmethod
    def add_device(ns_id, dev_id, device):
        """
        Adds device to the corresponding node of the TopologyMap

        Parameters
        ----------
        ns_id : str
            node id
        dev_id : str
            device id
        device : Device
            Object reference of Device class
        """
        # Acquire lock before entering
        with TopologyMap.lock:
            devices = TopologyMap.get_devices(ns_id)

            if ns_id is None:
                # Add into default namespace
                devices[dev_id] = device

            else:
                if dev_id in devices:
                    raise ValueError(
                        f"Device with id {dev_id} already present in namespace {ns_id}"
                    )

                devices[dev_id] = device
                if dev_id in TopologyMap.devices[DEFAULT_NAMESPACE_ID]:
                    # remove from default namespace
                    TopologyMap.delete_device(None, dev_id)

                TopologyMap.orphan_interfaces = TopologyMap.orphan_interfaces + 1

    @staticmethod
    def add_network(network):
        """
        Add network object reference to topology_map

        Parameters
        ----------
        network : Network
            Object reference of Network class
        """
        with TopologyMap.lock:
            TopologyMap.networks.append(network)

    @staticmethod
    def get_topology_map():
        """
        Get the entire topology map

        Returns
        -------
        Dict
        """
        with TopologyMap.lock:
            topology_map = {
                "nodes": TopologyMap.nodes,
                "devices": TopologyMap.devices,
                "hosts": TopologyMap.hosts,
                "routers": TopologyMap.routers,
            }

        return topology_map

    @staticmethod
    def get_nodes():
        """
        Get all the nodes of the TopologyMap

        Returns
        ------
        Dict
        """
        with TopologyMap.lock:
            nodes = TopologyMap.nodes

        return nodes

    @staticmethod
    def get_devices(ns_id):
        """
        Get the devices connected to a node

        Parameters
        ----------
        ns_id : str
            node id

        Returns
        -------
        Dict
        """
        with TopologyMap.lock:
            if ns_id is None:
                return TopologyMap.devices[DEFAULT_NAMESPACE_ID]

            if ns_id not in TopologyMap.devices:
                raise ValueError(
                    f"Namespace with id {ns_id} doesn't exist in TopologyMap"
                )

            devices = TopologyMap.devices[ns_id]

        return devices

    @staticmethod
    def get_routers():
        """
        Get all routers added

        Returns
        -------
        List
        """
        with TopologyMap.lock:
            routers = TopologyMap.routers

        return routers

    @staticmethod
    def get_hosts():
        """
        Get all hosts added

        Returns
        -------
        List
        """
        with TopologyMap.lock:
            hosts = TopologyMap.hosts

        return hosts

    @staticmethod
    def get_networks():
        """
        Get all networks

        Returns
        -------
        List
        """
        with TopologyMap.lock:
            networks = TopologyMap.networks

        return networks

    @staticmethod
    def get_node(ns_id):
        """
        Get a node

        Parameters
        ----------
        ns_id : str
            node id

        Returns
        -------
        Node Object
        """
        with TopologyMap.lock:
            if ns_id not in TopologyMap.nodes:
                raise ValueError(
                    f"Namespace with id {ns_id} doesn't exist in TopologyMap"
                )

            node = TopologyMap.nodes[ns_id]

        return node

    @staticmethod
    def get_device(ns_id, dev_id):
        """
        Get a device connected to a node

        Parameters
        ----------
        ns_id : str
            node id
        dev_id : str
            device id

        Returns
        -------
        Device Object
        """
        with TopologyMap.lock:
            if ns_id is None:
                if dev_id not in TopologyMap.devices[DEFAULT_NAMESPACE_ID]:
                    raise ValueError(
                        f"Device with id {dev_id} not present in default namespace"
                    )

                return TopologyMap.devices[DEFAULT_NAMESPACE_ID][dev_id]

            if ns_id not in TopologyMap.nodes:
                raise ValueError(
                    f"Namespace with id {ns_id} doesn't exist in TopologyMap"
                )

            if dev_id not in TopologyMap.devices[ns_id]:
                raise ValueError(
                    f"Device with id {dev_id} doesn't exist in namespace {ns_id}"
                )

            device = TopologyMap.devices[ns_id][dev_id]

        return device

    @staticmethod
    def get_qdiscs(ns_id, dev_id):
        """
        Get qdiscs associated with a device

        Parameters
        ----------
        ns_id : str
            node id
        dev_id : str
            device id

        Returns
        -------
        List
        """
        with TopologyMap.lock:
            device = TopologyMap.get_device(ns_id, dev_id)

        return device.qdisc_list

    @staticmethod
    def delete_all_mapping():
        """
        Delete all mapppings stored in TopologyMap

        """
        with TopologyMap.lock:
            TopologyMap.nodes = {}
            TopologyMap.devices = {DEFAULT_NAMESPACE_ID: {}}
            TopologyMap.hosts = []
            TopologyMap.routers = []
            TopologyMap.networks = []
            TopologyMap.orphan_interfaces = 0

    @staticmethod
    def dump():
        """
        Dump the TopologyMap. (for debugging purpose)

        """
        with TopologyMap.lock:
            topology_map = TopologyMap.get_topology_map()
            logger.debug("Config")
            logger.debug("------")
            logger.debug(json.dumps(topology_map, indent=4))

    @staticmethod
    def decrement_orphan_interfaces():
        """
        Reduce the orphan interface in the topology

        """
        with TopologyMap.lock:
            TopologyMap.orphan_interfaces = TopologyMap.orphan_interfaces - 1

    @staticmethod
    def delete_device(ns_id, dev_id):
        """
        Deletes a device from mentioned namespace

        Parameters
        ----------
        ns_id : str
            node id
        dev_id : str
            Device id which is deleted

        Returns
        -------
        Device Object
        """
        with TopologyMap.lock:
            # Get the device
            device = TopologyMap.get_device(ns_id, dev_id)

            # Delete the device from the namespace
            if ns_id is None:
                del TopologyMap.devices[DEFAULT_NAMESPACE_ID][dev_id]

            else:
                del TopologyMap.devices[ns_id][dev_id]
                TopologyMap.decrement_orphan_interfaces()

            return device

    @staticmethod
    def move_device(src_ns_id, dst_ns_id, dev_id):
        """
        Moves a device from one node to another

        Parameters
        ----------
        src_ns_id : str
            Source node id
        dst_ns_id : str
            Destination node id
        dev_id : str
            Device id which is moved
        """
        with TopologyMap.lock:
            device = TopologyMap.delete_device(src_ns_id, dev_id)
            TopologyMap.add_device(dst_ns_id, dev_id, device)
