# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2026 NITK Surathkal

"""Topology helper class for Gfc-2 topology"""

from nest import config
from nest.experiment import Flow
from nest.topology import Node, Router, connect
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper
from nest.routing.routing_helper import RoutingHelper

# This is a topology helper for the GFC-2 topology.
# The design for this GFC (Generic Fairness Configuration) is derived from the
# test configurations described in:
# Robert J. Simcoe,"Test configurations for fairness and other tests",
# ATM Forum/94-0557, July 1994.

# The network topology consists of 12 sender nodes (A1, A2, A3, B1, B2, B3, C, D, E, F, G, H),
# 8 receiver nodes (A, B, C, D, E, F, G, H) and 7 routers (R1, R2, R3, R4, R5, R6, R7).
#
# The customizations provided for the users who use the helper are:
#   * the number of flows between the senders and receivers
#   * the choice of qdiscs and its configurable attributes.
#
# This helper expects three parameters:
#   * exp = An Experiment object that should be created before this helper is used (mandatory)
#   * flows = A dictionary specifying the number and the kind of flows that the senders should send,
#             along with the duration of the flows (via the key "flow_duration")
#     (optional; if not provided, default values in the default_flows dictionary with TCP CUBIC will
#                be used)
#   * topology_config = A dictionary containing configuration options for the topology,
#     which includes:
#       - use_ipv6: A boolean flag indicating whether IPv6 addressing should be used
#           (default: True).
#           (optional; if not provided, IPv6 addresses will be used by default,
#                and if set to False, IPv4 addresses are used)
#       - enable_routing_logs: A boolean flag to enable or disable routing logs
#         (default: False).
#           (optional; if not provided, routing logs are disabled by default)
#       - use_dynamic_routing: A boolean flag to indicate whether to use dynamic routing (OSPF)
#                          or static routing (default: False)
#           (optional; if not provided, static routing is used by default, and if set to True,
#                OSPF is used for routing)
#
# If use_ipv6 flag is set to True, the following address type is used: 2001:i::/120
#   where i is the flow index (1, 2, 3, ...)
# - Example: 2001:1::/120, 2001:2::/120, 2001:3::/120
# - Each /120 subnet provides 256 addresses (2^8 host bits)
# - Usable for up to 256 addresses
#
# If use_ipv6 flag is set to False, the following addressing scheme is used: 192.168.i.0/24
#   where i is the flow index (1, 2, 3, ...)
# - Example: 192.168.1.0/24, 192.168.2.0/24, 192.168.3.0/24
# - Each /24 subnet provides 256 addresses (2^8 host bits)
# - Usable for up to 254 addresses (excluding network/broadcast)
#
# If use_dynamic_routing flag is set to True,
#    OSPF routing protocol is used for routing between the routers.
#
# If use_dynamic_routing flag is set to False,
#    static routes are set up between the nodes and routers.
#
# Example of flows dictionary:
#   flows = {
#       A1: { num_flows: 1, protocol: "tcp", tcp_type: "cubic" },
#       A2: { num_flows: 1, protocol: "tcp", tcp_type: "cubic" },
#       B1: { num_flows: 1, protocol: "udp"}, ...
#       "flow_duration": 400
#   }
#
# This helper maintains the following lists, for easy external access to all of the objects
# created in it:
# Note: The naming conventions are as per the diagram provided below.
#
#   * nodes = Dictionary containing all nodes created in the topology, it contains:
#       - senders = List of all sender nodes, stored in lexicographic order. They can be accessed
#         as nodes["senders"][0] for A1, nodes["senders"][1] for A2, ..., nodes["senders"][11] for H
#       - receivers = List of all receiver nodes, stored in lexicographic order.
#         They can be accessed as nodes["receivers"][0] for A, nodes["receivers"][1] for B,
#         nodes["receivers"][2] for C, ..., nodes["receivers"][7] for H
#       - routers = List of all routers, stored in left to right order. They can be accessed
#         as nodes["routers"][0] for R1, nodes["routers"][1] for R2, ..., nodes["routers"][6] for R7
#   * network_list = List of all network addresses created and used
#   * num_nodes = Dictionary containing the number of nodes of each type:
#       - senders = Number of sender nodes
#       - receivers = Number of receiver nodes
#       - routers = Number of router nodes
#   * interfaces = Dictionary containing all interfaces created in the topology, it contains:
#       - senders = List of interfaces on the sender nodes,
#          stored following the order of nodes["senders"] in lexicographic order:
#          eths1, eths2, .... eths12
#       - receivers = List of the interfaces of the receiver nodes,
#         stored following the order of nodes["receivers"] in lexicographic order:
#         ethr1, ethr2, .... ethr8
#       - routers = Nested list, where every i-th inner list is the
#         list of all interfaces of the i-th router, stored following the order of nodes["routers"].
#         The interfaces are stored in lexicographic order for each router, i.e.,
#         etr1a, etr1b, etr1c, etr1d for R1, etr2a, etr2b, etr2c, etr2d, etr2e, etr2f for R2, ...
#
# The helper contains the following methods to access the nodes and their interfaces:
#
#   - get_sender(index): returns the sender node at position 'index' in the list of sender nodes.
#     The nodes can be accessed lexicographically, i.e, A1 is at index 0,
#     A2 is at index 1, ..., H is at index 11
#
#   - get_receiver(index): returns the receiver node at position 'index',
#     in the list of receiver nodes. The nodes can be accessed lexicographically, i.e,
#     A is at index 0, B is at index 1, ..., H is at index 7
#
#   - get_router(index): returns the router node at position 'index' in the list of router nodes.
#     The nodes can be accessed in the order they are defined in the diagram, i.e, R1 is at index 0,
#     R2 is at index 1, ..., R7 is at index 6
#
#   - get_sender_interfaces(index): returns the interface for the sender at position 'index',
#     the interfaces are stored following the order of sender nodes: eths1, eths2, .... eths12
#
#   - get_receiver_interfaces(index): returns the interface for the receiver at position 'index',
#     the interfaces are stored following the order of receiver nodes: ethr1, ethr2, .... ethr8
#
#   - get_router_interfaces(index):
#     returns a list of all interfaces of the router at position 'index',
#     the router can be accessed in the order they are defined in the diagram,
#     i.e, R1 is at index 0, R2 is at index 1, ..., R7 is at index 6.
#     The returned list contains interfaces of the router in lexicographic order, i.e,
#     etr1a, etr1b, etr1c, etr1d for R1, etr2a, etr2b, etr2c, etr2d, etr2e, etr2f for R2, ...
#
# The following are the interfaces for reference:
#   * interfaces["senders"] = [eths1, eths2, .... eths12]
#   * interfaces["receivers"] = [ethr1, ethr2, .... ethr8]
#   * interfaces["routers"] = [[etr1a, etr1b, etr1c, etr1d],
#     [etr2a, etr2b, etr2c, etr2d, etr2e, etr2f], [etr3a, etr3b, etr3c, etr3d, etr3e],
#     [etr4a, etr4b, etr4c, etr4d, etr4e], [etr5a, etr5b, etr5c, etr5d],
#     [etr6a, etr6b, etr6c, etr6d, etr6e], [etr7a, etr7b, etr7c]]
#
# Note:
# When using set_attributes() to configure link parameters, always specify the qdisc explicitly.
# If omitted, pfifo is set as the default qdisc.
#
# #################################################################################################
#
#                                  Network Topology Diagram
#
# #################################################################################################
#
#   (s)            (r)            (r)            (r)            (r)        (r)      (r)      (r)
#   A1(1)          D(1)           E(2)           F(1)           H(2)       A(3)     C(3)     G(7)
#     |              |              |              |              |           \      /         |
#     |              |              |              |              |            \    /          |
#     |              |              |              |              |             \  /           |
#     |              |              |              |              |              \/            |
#     R1 ----------  R2 ----------- R3 ----------- R4 ----------  R5 ----------  R6 ---------  R7
#     /\            /|\             /\             /\             |              |             |
#    /  \          / | \           /  \           /  \            |              |             |
#   /    \        /  |  \         /    \         /    \           |              |             |
#  /      \      /   |   \       /      \       /      \          |              |             |
# B1(1)   D(1) E(2) A2(1) B2(1) A3(1)   F(1)   B3(1)   H(2)      C(3)           G(7)          B(3)
# (s)     (s)  (s)  (s)   (s)   (s)     (s)    (s)     (s)       (s)            (s)           (r)

# ===========================
# Network Topology Interfaces
# ===========================
# Flow Conventions:
# - All flows move from left to right
# - (3) indicates 3 parallel flows
# - (s) denotes a sender node
# - (r) denotes a receiver node
# - Assumption: IPv6 addressing is used
#
# Naming Conventions:
# - Sender interfaces are named as 'ethsX' where X is the sender node number
# - Receiver interfaces are named as 'ethrX' where X is the receiver node number
# - Router interfaces are named as 'etrXY', where X is the router number and,
#   Y is the interface identifier (a,b,c...)
#
#   Note: The interface names shown are for diagrammatic representation only.
#         The code does not assign these names to the interfaces.
#
# Interfaces of Senders:
#   - eths1  <-> Node A1(1)  (sender) (2001:1::/120) [50 Mbit/s, 4 ms]
#   - eths2  <-> Node A2(1)  (sender) (2001:2::/120) [50 Mbit/s, 4 ms]
#   - eths3  <-> Node A3(1)  (sender) (2001:3::/120) [50 Mbit/s, 4 ms]
#   - eths4  <-> Node B1(1)  (sender) (2001:4::/120) [50 Mbit/s, 4 ms]
#   - eths5  <-> Node B2(1)  (sender) (2001:5::/120) [50 Mbit/s, 4 ms]
#   - eths6  <-> Node B3(1)  (sender) (2001:6::/120) [50 Mbit/s, 4 ms]
#   - eths7  <-> Node C(3)   (sender) (2001:7::/120) [50 Mbit/s, 4 ms]
#   - eths8  <-> Node D(1)   (sender) (2001:8::/120) [50 Mbit/s, 4 ms]
#   - eths9  <-> Node E(2)   (sender) (2001:9::/120) [50 Mbit/s, 4 ms]
#   - eths10 <-> Node F(1)   (sender) (2001:10::/120) [50 Mbit/s, 4 ms]
#   - eths11 <-> Node G(7)   (sender) (2001:11::/120) [50 Mbit/s, 4 ms]
#   - eths12 <-> Node H(2)   (sender) (2001:12::/120) [50 Mbit/s, 4 ms]
#
# Interfaces of Receivers:
#   - ethr1  <-> Node A(3)   (receiver) (2001:19::/120) [50 Mbit/s, 4 ms]
#   - ethr2  <-> Node B(3)   (receiver) (2001:20::/120) [50 Mbit/s, 4 ms]
#   - ethr3  <-> Node C(3)   (receiver) (2001:21::/120) [50 Mbit/s, 4 ms]
#   - ethr4  <-> Node D(1)   (receiver) (2001:22::/120) [50 Mbit/s, 4 ms]
#   - ethr5  <-> Node E(2)   (receiver) (2001:23::/120) [50 Mbit/s, 4 ms]
#   - ethr6  <-> Node F(1)   (receiver) (2001:24::/120) [50 Mbit/s, 4 ms]
#   - ethr7  <-> Node G(7)   (receiver) (2001:25::/120) [50 Mbit/s, 4 ms]
#   - ethr8  <-> Node H(2)   (receiver) (2001:26::/120) [50 Mbit/s, 4 ms]
#
# Interfaces of R1:
# - etr1a <-> Node A1(1) (sender) [50 Mbit/s, 4 ms]
# - etr1b <-> Node B1(1) (sender) [50 Mbit/s, 4 ms]
# - etr1c <-> Node D(1)  (sender) [50 Mbit/s, 4 ms]
# - etr1d <-> R2:etr2d   (2001:13::/120) [50 Mbit/s, 13.33 ms]
#
# Interfaces of R2:
# - etr2a <-> Node A2(1) (sender) [50 Mbit/s, 4 ms]
# - etr2b <-> Node B2(1) (sender) [50 Mbit/s, 4 ms]
# - etr2c <-> Node E(2)  (sender) [50 Mbit/s, 4 ms]
# - etr2d <-> R1:etr1d   (2001:13::/120) [50 Mbit/s, 13.33 ms]
# - etr2e <-> R3:etr3c   (2001:14::/120) [100 Mbit/s, 6.67 ms]
# - etr2f <-> Node D(1)  (receiver) [50 Mbit/s, 4 ms]
#
# Interfaces of R3:
# - etr3a <-> Node A3(1) (sender) [50 Mbit/s, 4 ms]
# - etr3b <-> Node F(1)  (sender) [50 Mbit/s, 4 ms]
# - etr3c <-> R2:etr2e (2001:14::/120) [100 Mbit/s, 6.67 ms]
# - etr3d <-> R4:etr4c (2001:15::/120) [50 Mbit/s, 3.33 ms]
# - etr3e <-> Node E(2)  (receiver) [50 Mbit/s, 4 ms]
#
# Interfaces of R4:
# - etr4a <-> Node B3(1) (sender) [50 Mbit/s, 4 ms]
# - etr4b <-> Node H(2)  (sender) [50 Mbit/s, 4 ms]
# - etr4c <-> R3:etr3d (2001:15::/120) [50 Mbit/s, 3.33 ms]
# - etr4d <-> R5:etr5b (2001:16::/120) [150 Mbit/s, 3.33 ms]
# - etr4e <-> Node F(1)  (receiver) [50 Mbit/s, 4 ms]
#
# Interfaces of R5:
# - etr5a <-> Node C(3) (sender) [50 Mbit/s, 4 ms]
# - etr5b <-> R4:etr4d (2001:16::/120) [150 Mbit/s, 3.33 ms]
# - etr5c <-> R6:etr6b (2001:17::/120) [150 Mbit/s, 3.33 ms]
# - etr5d <-> Node H(2)  (receiver) [50 Mbit/s, 4 ms]
#
# Interfaces of R6:
# - etr6a <-> Node G(7) (sender) [50 Mbit/s, 4 ms]
# - etr6b <-> R5:etr5c (2001:17::/120) [150 Mbit/s, 3.33 ms]
# - etr6c <-> R7:etr7a (2001:18::/120) [50 Mbit/s, 6.67 ms]
# - etr6d <-> Node A(3)  (receiver) [50 Mbit/s, 4 ms]
# - etr6e <-> Node C(3)  (receiver) [50 Mbit/s, 4 ms]
#
# Interfaces of R7:
# - etr7a <-> R6:etr6c (2001:18::/120) [50 Mbit/s, 6.67 ms]
# - etr7b <-> Node B(3)  (receiver) [50 Mbit/s, 4 ms]
# - etr7c <-> Node G(7)  (receiver) [50 Mbit/s, 4 ms]
#
# #################################################################################################


class Gfc2Helper:
    """
    Helper class to create GFC-2 topology

    Attributes
    ----------
    nodes : dict {
                  "senders": list[Node],
                  "receivers": list[Node],
                  "routers": list[Node]
                  }
        Dictionary containing all nodes created in the topology

    network_list : list
        List of all network addresses created and used

    num_nodes : dict {"senders": int, "receivers": int, "routers": int}
        Dictionary containing the number of nodes of each type

    interfaces : dict {
                       "senders": list[Interface],
                       "receivers": list[Interface],
                       "routers": list[list[Interface]]
                       }
        Dictionary containing all interfaces created in the topology

    topology_config : dict {
                    "use_ipv6": bool,
                    "enable_routing_logs": bool,
                    "use_dynamic_routing": bool
                    }
            use_ipv6 : bool
                Flag indicating whether IPv6 addressing is used

            enable_routing_logs : bool
                Flag indicating whether routing logs are enabled

            use_dynamic_routing : bool
                Flag indicating whether dynamic routing (OSPF) is used or static routing is used

    net_count : int
        Counter to track the current network index while assigning addresses

    Methods
    -------
    __init__(exp, flows=None, use_ipv6=True, enable_routing_logs=False, use_dynamic_routing=False)
        Creates the GFC-2 topology with the given parameters

    _configure_globals()
        Configures global settings for the topology

    _create_nodes_and_routers()
        Creates sender nodes, receiver nodes, and routers

    _create_networks()
        Creates network addresses for the topology

    _connect_senders()
        Connects sender nodes to the routers

    _connect_routers()
        Connects routers to each other

    _connect_receivers()
        Connects receiver nodes to the routers

    _assign_addresses_and_default_routes()
        Assigns IP addresses and default routes to all nodes and routers

    _setup_static_routes(use_ipv6)
        Sets up static routes for all senders, receivers and routers

    _configure_links()
        Configures link attributes for all interfaces

    _setup_flows(exp, flows)
        Sets up the flows between senders and receivers based on the provided flow configuration

    """

    def __init__(self, exp, flows=None, topology_config=None):
        """
        Creates the GFC-2 topology with the given parameters:

        Parameters
        ----------
        exp : Experiment
            An Experiment object that should be created before this helper is used
        flows : dict, optional
            A dictionary specifying the number and the kind of flows that the senders should send,
            along with the duration of the flows
            (default: None, in which case all senders send TCP flows with cubic congestion control
             for 300 seconds each)
        topology_config : dict, optional
            A dictionary containing configuration options for the topology
            (default: None, in which case uses:
            {"use_ipv6": True, "enable_routing_logs": False, "use_dynamic_routing": False})
            - use_ipv6 : bool, optional
                A boolean flag indicating whether IPv6 addressing should be used (default: True).
            - enable_routing_logs : bool, optional
                A boolean flag to enable or disable routing logs
                (default: False, in which case routing logs are disabled)
            - use_dynamic_routing : bool, optional
                A boolean flag to indicate whether to use dynamic routing (OSPF) or static routing
                (default: False, in which case static routes are used instead of OSPF)
        """

        if flows is None:
            flows = {}

        self.nodes = {
            "senders": [],
            "receivers": [],
            "routers": [],
        }

        if topology_config is None:
            topology_config = {
                "use_ipv6": True,
                "enable_routing_logs": False,
                "use_dynamic_routing": False,
            }
        else:
            # Set default values for any missing keys in topology_config
            topology_config.setdefault("use_ipv6", True)
            topology_config.setdefault("enable_routing_logs", False)
            topology_config.setdefault("use_dynamic_routing", False)

        self.topology_config = topology_config
        self._configure_globals()
        self._create_nodes_and_routers()
        self._create_networks()
        self._connect_senders()
        self._connect_routers()
        self._connect_receivers()
        self._assign_addresses_and_default_routes()
        self._configure_links()
        self._setup_flows(exp, flows)

    def _configure_globals(self):
        """
        Configures global settings for the topology
        """
        # Using FRR (Free Range Routing) as the routing suite,
        # to be able to use routing protocols like OSPF
        if self.topology_config["use_dynamic_routing"]:
            config.set_value("routing_suite", "frr")
            config.set_value(
                "routing_logs", self.topology_config["enable_routing_logs"]
            )

    def _create_nodes_and_routers(self):
        """
        Creates sender nodes, receiver nodes, and routers
        """
        self.num_nodes = {
            "senders": 12,
            "receivers": 8,
            "routers": 7,
        }

        # Creating sender and receiver nodes
        senders = []
        for i in range(8):
            if i < 2:
                senders.extend([Node(f"{chr(65+i)}{j+1}") for j in range(3)])
            else:
                senders.append(Node(f"{chr(65+i)}"))
        self.nodes["senders"] = senders

        self.nodes["receivers"] = [
            Node(chr(65 + i)) for i in range(self.num_nodes["receivers"])
        ]

        # Creating routers
        self.nodes["routers"] = [
            Router("r" + str(i + 1)) for i in range(self.num_nodes["routers"])
        ]

        self.interfaces = {
            "senders": [],
            "receivers": [],
            "routers": [[] for _ in range(self.num_nodes["routers"])],
        }

    def _create_networks(self):
        """
        Creates network addresses for the topology
        """

        # Creating network addresses based on the addressing scheme
        count = (
            self.num_nodes["senders"]
            + self.num_nodes["receivers"]
            + self.num_nodes["routers"]
            - 1
        )
        if self.topology_config["use_ipv6"]:
            self.network_list = [
                Network(f"2001:{i}::/120") for i in range(1, count + 1)
            ]
        else:
            self.network_list = [
                Network(f"192.168.{i}.0/24") for i in range(1, count + 1)
            ]

        # Counter to track the current network index while assigning addresses
        self.net_count = 0

    def _connect_senders(self):
        """
        Connects sender nodes to the routers
        """
        # sender_router_map defines the sender-to-router connectivity
        sender_router_map = [
            (0, 0),
            (1, 1),
            (2, 2),
            (3, 0),
            (4, 1),
            (5, 3),
            (6, 4),
            (7, 0),
            (8, 1),
            (9, 2),
            (10, 5),
            (11, 3),
        ]
        for sender_id, router_id in sender_router_map:
            sender_interface, router_interface = connect(
                self.nodes["senders"][sender_id],
                self.nodes["routers"][router_id],
                network=self.network_list[self.net_count],
            )
            self.interfaces["senders"].append(sender_interface)
            self.interfaces["routers"][router_id].append(router_interface)
            self.net_count += 1

    def _connect_routers(self):
        """
        Connects routers to each other
        """
        # router_router_map defines the router-to-router connectivity
        router_router_map = [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 5),
            (5, 6),
        ]

        for router1_id, router2_id in router_router_map:
            router1_interface, router2_interface = connect(
                self.nodes["routers"][router1_id],
                self.nodes["routers"][router2_id],
                network=self.network_list[self.net_count],
            )
            self.interfaces["routers"][router1_id].append(router1_interface)
            self.interfaces["routers"][router2_id].append(router2_interface)
            self.net_count += 1

    def _connect_receivers(self):
        """
        Connects receiver nodes to the routers
        """
        # receiver_router_map defines the receiver-to-router connectivity
        receiver_router_map = [
            (0, 5),
            (1, 6),
            (2, 5),
            (3, 1),
            (4, 2),
            (5, 3),
            (6, 6),
            (7, 4),
        ]

        for receiver_id, router_id in receiver_router_map:
            receiver_interface, router_interface = connect(
                self.nodes["receivers"][receiver_id],
                self.nodes["routers"][router_id],
                network=self.network_list[self.net_count],
            )
            self.interfaces["receivers"].append(receiver_interface)
            self.interfaces["routers"][router_id].append(router_interface)
            self.net_count += 1

    def _assign_addresses_and_default_routes(self):
        """
        Assigns IP addresses and default routes to all nodes and routers
        """
        AddressHelper.assign_addresses()

        # Adding default routes for all the nodes and routers

        # Senders
        for i in range(self.num_nodes["senders"]):
            self.nodes["senders"][i].add_route("DEFAULT", self.interfaces["senders"][i])

        # Receivers
        for i in range(self.num_nodes["receivers"]):
            self.nodes["receivers"][i].add_route(
                "DEFAULT", self.interfaces["receivers"][i]
            )

        if self.topology_config["use_dynamic_routing"]:
            # Using OSPF routing protocol for setting the routes on the routers
            RoutingHelper(
                protocol="ospf", ipv6_routing=self.topology_config["use_ipv6"]
            ).populate_routing_tables()
        else:
            self._setup_static_routes(self.topology_config["use_ipv6"])

    def _setup_static_routes(self, use_ipv6):
        """
        Sets up static routes for all routers in the GFC-2 topology.

        Network address assignment order
        (derived from _connect_senders → _connect_routers → _connect_receivers):

        Sender networks (net indices 1-12):
          net 1  : A1 <-> R1   net 2  : A2 <-> R2   net 3  : A3 <-> R3
          net 4  : B1 <-> R1   net 5  : B2 <-> R2   net 6  : B3 <-> R4
          net 7  : C  <-> R5   net 8  : D  <-> R1   net 9  : E  <-> R2
          net 10 : F  <-> R3   net 11 : G  <-> R6   net 12 : H  <-> R4

        Router-router networks (net indices 13-18):
          net 13 : R1 <-> R2   net 14 : R2 <-> R3   net 15 : R3 <-> R4
          net 16 : R4 <-> R5   net 17 : R5 <-> R6   net 18 : R6 <-> R7

        Receiver networks (net indices 19-26):
          net 19 : rA <-> R6   net 20 : rB <-> R7   net 21 : rC <-> R6
          net 22 : rD <-> R2   net 23 : rE <-> R3   net 24 : rF <-> R4
          net 25 : rG <-> R7   net 26 : rH <-> R5
        """

        def net(index):
            if use_ipv6:
                return f"2001:{index}::/120"
            return f"192.168.{index}.0/24"

        # Convenience aliases
        r_1 = self.interfaces["routers"][0]  # [0:→A1, 1:→B1, 2:→D,  3:→R2]
        r_2 = self.interfaces["routers"][
            1
        ]  # [0:→A2, 1:→B2, 2:→E,  3:→R1, 4:→R3, 5:→rD]
        r_3 = self.interfaces["routers"][2]  # [0:→A3, 1:→F,  2:→R2, 3:→R4, 4:→rE]
        r_4 = self.interfaces["routers"][3]  # [0:→B3, 1:→H,  2:→R3, 3:→R5, 4:→rF]
        r_5 = self.interfaces["routers"][4]  # [0:→C,  1:→R4, 2:→R6, 3:→rH]
        r_6 = self.interfaces["routers"][5]  # [0:→G,  1:→R5, 2:→R7, 3:→rA, 4:→rC]
        r_7 = self.interfaces["routers"][6]  # [0:→R6, 1:→rB, 2:→rG]

        # Attach Routes to R1
        # Directly attached sender networks
        self.nodes["routers"][0].add_route(net(1), r_1[0])  # A1 via etr1a
        self.nodes["routers"][0].add_route(net(4), r_1[1])  # B1 via etr1b
        self.nodes["routers"][0].add_route(net(8), r_1[2])  # D  via etr1c
        # Everything else goes forward via R2
        for idx in [2, 3, 5, 6, 7, 9, 10, 11, 12, 19, 20, 21, 22, 23, 24, 25, 26]:
            self.nodes["routers"][0].add_route(net(idx), r_1[3])

        # Attach Routes to R2
        # Directly attached sender networks
        self.nodes["routers"][1].add_route(net(2), r_2[0])  # A2 via etr2a
        self.nodes["routers"][1].add_route(net(5), r_2[1])  # B2 via etr2b
        self.nodes["routers"][1].add_route(net(9), r_2[2])  # E  via etr2c
        # Directly attached receiver network
        self.nodes["routers"][1].add_route(net(22), r_2[5])  # rD via etr2f
        # A1, B1, D are behind R1 — go back via R1
        for idx in [1, 4, 8]:
            self.nodes["routers"][1].add_route(net(idx), r_2[3])
        # A3, B3, C, F, G, H and receivers rA, rB, rC, rE, rF, rG, rH — go forward via R3
        for idx in [3, 6, 7, 10, 11, 12, 19, 20, 21, 23, 24, 25, 26]:
            self.nodes["routers"][1].add_route(net(idx), r_2[4])

        # Attach Routes to R3
        # Directly attached sender networks
        self.nodes["routers"][2].add_route(net(3), r_3[0])  # A3 via etr3a
        self.nodes["routers"][2].add_route(net(10), r_3[1])  # F  via etr3b
        # Directly attached receiver network
        self.nodes["routers"][2].add_route(net(23), r_3[4])  # rE via etr3e
        # A1, A2, B1, B2, D, E and rD are behind R2 — go back via R2
        for idx in [1, 2, 4, 5, 8, 9, 22]:
            self.nodes["routers"][2].add_route(net(idx), r_3[2])
        # B3, C, G, H and receivers rA, rB, rC, rF, rG, rH — go forward via R4
        for idx in [6, 7, 11, 12, 19, 20, 21, 24, 25, 26]:
            self.nodes["routers"][2].add_route(net(idx), r_3[3])

        # Attach Routes to R4
        # Directly attached sender networks
        self.nodes["routers"][3].add_route(net(6), r_4[0])  # B3 via etr4a
        self.nodes["routers"][3].add_route(net(12), r_4[1])  # H  via etr4b
        # Directly attached receiver network
        self.nodes["routers"][3].add_route(net(24), r_4[4])  # rF via etr4e
        # A1-A3, B1-B2, D, E, F and rD, rE are behind R3 — go back via R3
        for idx in [1, 2, 3, 4, 5, 8, 9, 10, 22, 23]:
            self.nodes["routers"][3].add_route(net(idx), r_4[2])
        # C, G and receivers rA, rB, rC, rG, rH — go forward via R5
        for idx in [7, 11, 19, 20, 21, 25, 26]:
            self.nodes["routers"][3].add_route(net(idx), r_4[3])

        # Attach Routes to R5
        # Directly attached sender network
        self.nodes["routers"][4].add_route(net(7), r_5[0])  # C  via etr5a
        # Directly attached receiver network
        self.nodes["routers"][4].add_route(net(26), r_5[3])  # rH via etr5d
        # A1-A3, B1-B3, D, E, F, H and rD, rE, rF are behind R4 — go back via R4
        for idx in [1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 22, 23, 24]:
            self.nodes["routers"][4].add_route(net(idx), r_5[1])
        # G and receivers rA, rB, rC, rG — go forward via R6
        for idx in [11, 19, 20, 21, 25]:
            self.nodes["routers"][4].add_route(net(idx), r_5[2])

        # Attach Routes to R6
        # Directly attached sender network
        self.nodes["routers"][5].add_route(net(11), r_6[0])  # G  via etr6a
        # Directly attached receiver networks
        self.nodes["routers"][5].add_route(net(19), r_6[3])  # rA via etr6d
        self.nodes["routers"][5].add_route(net(21), r_6[4])  # rC via etr6e
        # All senders except G, and rD, rE, rF, rH are behind R5 — go back via R5
        for idx in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 22, 23, 24, 26]:
            self.nodes["routers"][5].add_route(net(idx), r_6[1])
        # rB, rG are ahead at R7 — go forward via R7
        for idx in [20, 25]:
            self.nodes["routers"][5].add_route(net(idx), r_6[2])

        # Attach Routes to R7
        # Directly attached receiver networks
        self.nodes["routers"][6].add_route(net(20), r_7[1])  # rB via etr7b
        self.nodes["routers"][6].add_route(net(25), r_7[2])  # rG via etr7c
        # Everything else is behind R6 — go back via R6
        for idx in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 19, 21, 22, 23, 24, 26]:
            self.nodes["routers"][6].add_route(net(idx), r_7[0])

    def _configure_links(self):
        """
        Configures link attributes for all interfaces
        """
        link_bandwidth = "50mbit"
        link_latency = "4ms"
        qdisc = "pfifo"

        # Setting default attributes for interfaces of senders
        for iface in self.interfaces["senders"]:
            iface.set_attributes(link_bandwidth, link_latency, qdisc)

        # Setting default attributes for interfaces of receivers
        for iface in self.interfaces["receivers"]:
            iface.set_attributes(link_bandwidth, link_latency)

        # Setting default attributes for interfaces of routers
        for router_interface_list in self.interfaces["routers"]:
            for interface in router_interface_list:
                interface.set_attributes(link_bandwidth, link_latency, qdisc)

        # Setting default attributes for inter-router links
        router_config = [
            (0, 3, "50mbit", "53.32ms"),
            (1, 3, "50mbit", "53.32ms"),
            (1, 4, "150mbit", "26.68ms"),
            (2, 2, "150mbit", "26.68ms"),
            (2, 3, "150mbit", "13.32ms"),
            (3, 2, "150mbit", "13.32ms"),
            (3, 3, "100mbit", "13.32ms"),
            (4, 1, "100mbit", "13.32ms"),
            (4, 2, "100mbit", "13.32ms"),
            (5, 1, "100mbit", "13.32ms"),
            (5, 2, "100mbit", "26.68ms"),
            (6, 0, "100mbit", "26.68ms"),
        ]

        for router_id, interface_id, bandwidth, delay in router_config:
            self.interfaces["routers"][router_id][interface_id].set_attributes(
                bandwidth, delay, qdisc
            )

    def _setup_flows(self, exp, flows):
        """
        Sets up the flows between senders and receivers based on the provided flow configuration

        Parameters
        ----------
        exp : Experiment
            An Experiment object that should be created before this helper is used
        flows : dict
            A dictionary specifying the number and the kind of flows that the senders should send,
            along with the duration of the flows
        """
        default_flows = {
            "A1": 1,
            "A2": 1,
            "A3": 1,
            "B1": 1,
            "B2": 1,
            "B3": 1,
            "C": 1,
            "D": 1,
            "E": 2,
            "F": 1,
            "G": 7,
            "H": 2,
        }

        # Adding flows
        for i, (node, value) in enumerate(default_flows.items()):

            num_flows = flows.get(node, {}).get("num_flows", value)
            protocol = flows.get(node, {}).get("protocol", "tcp")
            if protocol == "tcp":
                tcp_type = flows.get(node, {}).get("tcp_type", "cubic")

            # Mapping each sender to a receiver based on the topology pattern
            # - Senders A1, A2, A3 -> receiver A (receiver_id = 0)
            # - Senders B1, B2, B3 -> receiver B (receiver_id = 1)
            # - Remaining senders (C, D, E, F, G, H) -> receivers starting from C
            #                                           (receiver_id = i - 4)
            receiver_id = i - 4
            if i < 3:
                receiver_id = 0
            elif i < 6:
                receiver_id = 1

            # Setting flow duration for all flows
            # The default is 300 seconds, but can be overridden
            flow_duration = flows.get("flow_duration", 300)

            vars()["flow" + str(i + 1)] = Flow(
                self.nodes["senders"][i],
                self.nodes["receivers"][receiver_id],
                self.interfaces["receivers"][receiver_id].get_address(),
                i,
                flow_duration + i,
                num_flows,
            )

            if protocol == "tcp":
                exp.add_tcp_flow(vars()["flow" + str(i + 1)], tcp_type)
            elif protocol == "udp":
                exp.add_udp_flow(vars()["flow" + str(i + 1)])
            else:
                raise ValueError(f"Unsupported protocol: {protocol}")

    def get_sender(self, index):
        """
        Returns the sender node at the specified index
        """
        return self.nodes["senders"][index]

    def get_receiver(self, index):
        """
        Returns the receiver node at the specified index
        """
        return self.nodes["receivers"][index]

    def get_router(self, index):
        """
        Returns the router node at the specified index
        """
        return self.nodes["routers"][index]

    def get_sender_interface(self, index):
        """
        Returns the sender interface at the specified index
        """
        return self.interfaces["senders"][index]

    def get_receiver_interface(self, index):
        """
        Returns the receiver interface at the specified index
        """
        return self.interfaces["receivers"][index]

    def get_router_interface(self, router_index, interface_index):
        """
        Returns the router interface at the specified router and interface indices
        """
        return self.interfaces["routers"][router_index][interface_index]
