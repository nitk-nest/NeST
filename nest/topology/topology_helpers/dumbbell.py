# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""Topology helper class for Dumbbell topologies"""

from nest import config
from nest.topology import Node, Router, connect
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper
from nest.routing.routing_helper import RoutingHelper

# This helper helps users to create dumbbell topologies easily.
# A dumbbell topology consists of two sets of nodes connected to a router each, and these
# two routers can be connected to each other directly or through multiple other routers in
# the same path linearly. The nodes connected to the left-most router are called the left side
# nodes, while those connected to the right-most router are called as the right side nodes.
# This helper expects a dictionary consisting of the number of left side nodes, the number of
# right side nodes and the number of routers, a flag to denote whether IPv6 addresses should
# be used or not, and a flag to enable FRR logging as input parameters. This helper creates the
# nodes and the routers, assigns appropriate network addresses to the sub-networks, adds default
# routes for each of the devices and sets default attributes (bandwidth: 10mbit,
# delay: 4ms, qdisc: pfifo) to the interfaces.

# The OSPF routing protocol from the FRR suite is used for setting up the routes in the network.

# By default, the networks created in this helper use IPv6 addresses of the form: 2001:i::/120,
# where i is the network index (for example, 2001:1::/120, 2001:2::/120, etc.). If the IPv6
# input parameter (use_ipv6) is set to False, IPv4 addresses of the form: 192.168.(i+1).0/24
# are used, where i is the network index (for example, 192.168.1.0/24, 192.168.2.0/24, etc.).
# Each of these represent subnets providing 256 addresses (from 2^8 host bits). In the case
# of IPv4, only 254 of these addresses can be assigned to nodes after excluding the
# network address and the broadcast address.

# This helper maintains the following lists grouped in the dictionaries "nodes" and "interfaces" for
# easy external access to all of the objects created in this helper:
#
# * nodes["left_node_list"] = List of left side nodes, stored from top to bottom
#   (named as lh1, lh2, and so on)
#
# * nodes["right_node_list"] = List of right side nodes, stored from top to bottom
#   (named as rh1, rh2, and so on)
#
# * nodes["router_list"] = List of all routers, stored from left to right
#   (named as r1, r2, and so on)
#
# * network_list = List of all network addresses created and used
#
# * interfaces["left_interfaces"] = List of the interfaces on the left side nodes,
#   stored following the order of left_node_list
#   (named as etlh1, etlh2, and so on {from 'et' + node_name})
#
# * interfaces["right_interfaces"] = List of the interfaces on the right side nodes,
#   stored following the order of right_node_list
#   (named as etrh1, etrh2, and so on {from 'et' + node_name})
#
# * interfaces["router_interfaces"] = Nested list, where every i-th inner list is the list
#   of all interfaces on the i-th router, stored following the order of router_list
#   (named as etr1a, etr1b, and so on {from 'et' + router_name + letter, where
#   letters like a, b, c, etc. are used to distinguish between the interfaces
#   on a single router, and they are assigned in numeric order of the
#   neighbours they connect to, following the order of left side nodes,
#   followed by routers, followed by right side nodes})

# These can be accessed outside this helper file using the getter-methods included in this class.
#
# Note: Whenever the attributes of an interface are changed outside this helper using
# the set_attributes() method, the qdisc must be specified, with "pfifo" being used
# if a specific qdisc is not required; otherwise, kernel defaults would be applied.


#####################################################################################
#   Network Topology ('m' left side nodes, 'n' right side nodes and 'l' routers)    #
#                                                                                   #
#                                                                                   #
# lh1 -------------------|                                   |--------------- rh1   #
#                        |                                   |                      #
# lh2 -------------------|                                   |--------------- rh2   #
#  .                     |                                   |                 .    #
#  .                     |                                   |                 .    #
#  .                     r1 --- r2 ----......---- r(l-1)--- rl                 .    #
#  .                     |                                   |                 .    #
#  .                     |                                   |                 .    #
# lh(m-1) ---------------|                                   |--------------rh(n-1) #
#                        |                                   |                      #
# lhm -------------------|                                   |----------------rhn   #
#                                                                                   #
#                                                                                   #
#####################################################################################


class DumbbellHelper:

    """
    Helper to create dumbbell topologies.

    Attributes
    ----------
    num_nodes: dict{"left": int, "right": int, "routers": int}
        Dictionary of number of nodes for left-side nodes, right-side nodes and routers

    net_count: int
        Number of network addresses assigned so far

    nodes: dict{"left_node_list": list[Node], "right_node_list": list[Node],
            "router_list": list[Router]}
        Dictionary of lists of nodes for left side nodes, right side nodes and routers

    interfaces: dict{"left_interfaces": list[Interface], "right_interfaces": list[Interface],
                        "router_interfaces": list[list[Interface]}
        Dictionary of lists of interfaces assigned to left side nodes, right side nodes and
        a nested list for routers (grouped by routers)

    network_list: list[Network]
        List of networks assigned to this topology
    """

    def __init__(
        self,
        num_nodes: dict,
        use_ipv6=True,
        enable_frr_logging=False,
    ):
        """
        Create a dumbbell network with the given number of left and right side nodes and routers.

        Parameters
        ----------
        num_nodes: dict{"left": int, "right": int, "routers": int}
            Dictionary of number of nodes for left-side nodes, right-side nodes and routers

        use_ipv6: boolean
            Flag to indicate whether IPv6 addresses should be used instead of IPv4 addresses

        enable_frr_logging: boolean
            Flag to enable FRR logging
        """

        if num_nodes["left"] < 1:
            raise ValueError("Number of left side nodes should be at least 1")
        if num_nodes["right"] < 1:
            raise ValueError("Number of right side nodes should be at least 1")
        if num_nodes["routers"] < 2:
            raise ValueError("Number of routers should be at least 2")

        self.num_nodes = num_nodes

        self.nodes = {}

        self.net_count = 0

        self.interfaces = {}
        # left_interfaces: list of the interfaces on the left side nodes
        self.interfaces["left_interfaces"] = []
        # right_interfaces: list of the interfaces on the right side nodes
        self.interfaces["right_interfaces"] = []
        # router_interfaces: nested list of the interfaces on the routers, grouped by routers
        self.interfaces["router_interfaces"] = [[]]

        # Creating the topology
        self._configure_globals(enable_frr_logging)
        self._create_nodes_and_routers()
        self._create_networks(use_ipv6)
        self._connect_senders()
        self._connect_routers()
        self._connect_receivers()
        self._assign_addresses_and_default_routes(use_ipv6)
        self._configure_links()

    def _configure_globals(self, enable_frr_logging):
        """
        Configure the routing suite and enable/disable the logging

        Parameters
        ----------
        enable_frr_logging: boolean
            Flag to indicate whether FRR logging must be enabled or not
        """
        # Using FRR (Free Range Routing) as the routing suite
        # to be able to use routing protocols like OSPF
        config.set_value("routing_suite", "frr")
        config.set_value("routing_logs", enable_frr_logging)

    def _create_nodes_and_routers(self):
        """
        Create the left nodes, right nodes and routers
        """
        num_left_nodes = self.num_nodes["left"]
        num_right_nodes = self.num_nodes["right"]
        num_routers = self.num_nodes["routers"]

        # Creating Nodes
        self.nodes["left_node_list"] = [
            Node("lh" + str(i + 1)) for i in range(num_left_nodes)
        ]
        self.nodes["right_node_list"] = [
            Node("rh" + str(i + 1)) for i in range(num_right_nodes)
        ]

        # Creating Routers
        self.nodes["router_list"] = [
            Router("r" + str(i + 1)) for i in range(num_routers)
        ]

    def _create_networks(self, use_ipv6):
        """
        Create the network addresses

        Parameters
        ----------
        use_ipv6: boolean
            If 'True', use IPv6 addresses, else use IPv4 addresses
        """
        num_left_nodes = self.num_nodes["left"]
        num_right_nodes = self.num_nodes["right"]
        num_routers = self.num_nodes["routers"]

        if use_ipv6:
            # Creating IPv6 network addresses
            self.network_list = [
                Network("2001:" + str(i + 1) + "::/120")
                for i in range(num_left_nodes + num_right_nodes + num_routers - 1)
            ]
        else:
            # Creating IPv4 network addresses
            self.network_list = [
                Network("192.168." + str(i + 1) + ".0/24")
                for i in range(num_left_nodes + num_right_nodes + num_routers - 1)
            ]

    def _connect_senders(self):
        """
        Connect left side nodes to the left-most router
        """
        num_left_nodes = self.num_nodes["left"]

        for i in range(num_left_nodes):

            vars()["etlh" + str(i + 1)], vars()["etr1" + chr(97 + i)] = connect(
                self.nodes["left_node_list"][i],
                self.nodes["router_list"][0],
                network=self.network_list[self.net_count],
            )

            self.interfaces["left_interfaces"].append(vars()["etlh" + str(i + 1)])
            self.interfaces["router_interfaces"][0].append(vars()["etr1" + chr(97 + i)])

            self.net_count += 1

    def _connect_routers(self):
        """
        Connect the routers to each other
        """
        num_left_nodes = self.num_nodes["left"]
        num_routers = self.num_nodes["routers"]

        for i in range(num_routers - 1):

            if i == 0:
                (vars()["etr1" + chr(97 + num_left_nodes)], etr2a) = connect(
                    self.nodes["router_list"][0],
                    self.nodes["router_list"][1],
                    network=self.network_list[self.net_count],
                )

                self.interfaces["router_interfaces"][0].append(
                    vars()["etr1" + chr(97 + num_left_nodes)]
                )

                self.interfaces["router_interfaces"].append([etr2a])

            else:
                (
                    vars()["etr" + str(i + 1) + "b"],
                    vars()["etr" + str(i + 2) + "a"],
                ) = connect(
                    self.nodes["router_list"][i],
                    self.nodes["router_list"][i + 1],
                    network=self.network_list[self.net_count],
                )

                self.interfaces["router_interfaces"][-1].append(
                    vars()["etr" + str(i + 1) + "b"]
                )

                self.interfaces["router_interfaces"].append(
                    [vars()["etr" + str(i + 2) + "a"]]
                )

            self.net_count += 1

    def _connect_receivers(self):
        """
        Connect right side nodes to the right-most router
        """
        num_right_nodes = self.num_nodes["right"]
        num_routers = self.num_nodes["routers"]

        for i in range(num_right_nodes):
            (
                vars()["etrh" + str(i + 1)],
                vars()["etr" + str(num_routers) + chr(97 + i + 1)],
            ) = connect(
                self.nodes["right_node_list"][i],
                self.nodes["router_list"][num_routers - 1],
                network=self.network_list[self.net_count],
            )

            self.interfaces["router_interfaces"][-1].append(
                vars()["etr" + str(num_routers) + chr(97 + i + 1)]
            )

            self.interfaces["right_interfaces"].append(vars()["etrh" + str(i + 1)])

            self.net_count += 1

    def _assign_addresses_and_default_routes(self, use_ipv6):
        """
        Assign addresses, add default routes for the nodes and use OSPF routing for the routers

        Parameters
        ----------
        use_ipv6: boolean
            If 'True', use IPv6 addresses, else use IPv4 addresses
        """
        # Assigning addresses
        AddressHelper.assign_addresses()

        # Adding default routes for all the nodes

        # Left side nodes
        for i, interface in enumerate(self.interfaces["left_interfaces"]):
            self.nodes["left_node_list"][i].add_route("DEFAULT", interface)

        # Right side nodes
        for i, interface in enumerate(self.interfaces["right_interfaces"]):
            self.nodes["right_node_list"][i].add_route("DEFAULT", interface)

        # Using OSPF routing protocol for setting the routes on the routers
        RoutingHelper(protocol="ospf", ipv6_routing=use_ipv6).populate_routing_tables()

    def _configure_links(self):
        """
        Set default attributes (bandwidth of 10mbit, delay of 4ms and PFIFO qdisc)
        to the interfaces
        """
        qdisc = "pfifo"

        # Interfaces on the left side nodes
        for i in range(len(self.interfaces["left_interfaces"])):
            self.interfaces["left_interfaces"][i].set_attributes("10mbit", "4ms", qdisc)

        # Interfaces on the right side nodes
        for i in range(len(self.interfaces["right_interfaces"])):
            self.interfaces["right_interfaces"][i].set_attributes(
                "10mbit", "4ms", qdisc
            )

        # Interfaces on the routers
        for router_interface_list in self.interfaces["router_interfaces"]:
            for interface in router_interface_list:
                interface.set_attributes("10mbit", "4ms", qdisc)

    def get_left_node(self, index: int):
        """
        Get the left side node present at the given index
        """
        return self.nodes["left_node_list"][index]

    def get_right_node(self, index: int):
        """
        Get the right side node present at the given index
        """
        return self.nodes["right_node_list"][index]

    def get_router(self, index: int):
        """
        Get the router present at the given index
        """
        return self.nodes["router_list"][index]

    def get_network_list(self, index: int):
        """
        Get the i-th network of the topology
        """
        return self.network_list[index]

    def get_left_interface(self, index: int):
        """
        Get the interface on the left side node present at the given index
        """
        return self.interfaces["left_interfaces"][index]

    def get_right_interface(self, index: int):
        """
        Get the interface on the right side node present at the given index
        """
        return self.interfaces["right_interfaces"][index]

    def get_router_interface(self, router_index: int, interface_index: int):
        """
        Get the interface_index-th interface on the router present at the given router_index
        """
        return self.interfaces["router_interfaces"][router_index][interface_index]
