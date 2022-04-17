# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""Class to handle static routing related functionalities"""

from nest.topology_map import TopologyMap


class StaticRouting:
    """
    Handles Static Routing related fuctionalities
    """

    def __init__(self):
        # reverse mapping from interface to node, used during DFS
        self._interface_to_node_map = {}

        for host in TopologyMap.get_hosts():
            for interface in host.interfaces:
                self._interface_to_node_map[interface.address] = host

        for router in TopologyMap.get_routers():
            for interface in router.interfaces:
                self._interface_to_node_map[interface.address] = router

    def dfs(self, cur_node, dest_address, visited):
        """
        Run dfs for a given node and populate routing table entries keeping
        this node as destination. dfs also works if the topology has cycles,
        the algorithm will use a spanning tree for routing.

        Parameters
        ----------
        cur_node : Node
            The current node at which dfs is to be run
        start_node : Node
            The root node from which the dfs is run initially
        visited : Set(Node._id)
            The set of ids of all nodes visited during the dfs
        """

        for interface in cur_node.interfaces:
            interface_pair = interface.pair
            next_node = self._interface_to_node_map[interface_pair.address]

            if next_node.id not in visited:
                visited.add(next_node.id)
                next_node.add_route(
                    dest_addr=dest_address,
                    via_interface=interface_pair,
                    next_hop_addr=interface.address,
                )
                self.dfs(next_node, dest_address, visited)

    def run_static_routing(self):
        """
        Iterate through all hosts and call dfs for them
        """

        for start_node in TopologyMap.get_hosts():
            if len(start_node.interfaces) == 0:
                # a single host not connected to any router or host
                continue

            # we assume that a single host will be connected to only one router
            self.dfs(
                cur_node=start_node,
                dest_address=start_node.interfaces[0].address,
                visited=set(),
            )
