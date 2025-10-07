# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""Topology helper class for GFC-1 topology"""

from nest import config
from nest.topology import Node, Router, connect
from nest.experiment import Flow
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper
from nest.routing.routing_helper import RoutingHelper

# This is a topology helper for the GFC-1 topology.
# The network topology consists of 6 sender nodes (A, B, C, D, E, F),
# 6 receiver nodes (A, B, C, D, E, F) and 5 routers (R1, R2, R3, R4, R5).
#
# The customizations provided for the users who use the helper are:
#   * the number of flows between the senders and receivers
#   * the choice of qdiscs and its configurable attributes.
#
# This helper expects four parameters:
#   * exp = An Experiment object that should be created before this helper is used (mandatory)
#   * flows = A dictionary specifying the number and the kind of flows that the senders should send,
#             along with the flow duration (via the key "flow_duration").
#     (optional; if not provided, default values in the default_flows dictionary with TCP CUBIC will
#                be used)
#   * use_ipv6: A boolean flag indicating whether IPv6 addressing should be used (default: True).
#     (optional; if not provided, IPv6 addresses will be used by default,
#                and if set to False, IPv4 addresses are used)
#   * enable_routing_logs: A boolean flag to enable or disable routing logs (default: False).
#     (optional; if not provided, routing logs are disabled by default)
#
# If use_ipv6 flag is set to True, the following address type is used: 2001:i::/120
#   where i is the flow index (1, 2, 3, ...)
# - Example: 2001:1::/120, 2001:2::/120, 2001:3::/120
# - Each /120 subnet provides 256 addresses (2^8 host bits)
# - Usable for up to 256 nodes.
#
# If use_ipv6 flag is set to False, the following address type is used: 192.168.i.0/24
#   where i is the flow index (1, 2, 3, ...)
# - Example: 192.168.1.0/24, 192.168.2.0/24, 192.168.3.0/24
# - Each /24 subnet provides 256 addresses (2^8 host bits)
# - Usable for up to 254 nodes (excluding network/broadcast)
#
# The OSPF routing protocol from the FRR suite is used for setting up the routes in the network.
#
# Example of flows dictionary:
#   flows = {
#       A: { num_flows: 1, protocol: "tcp", tcp_type: "cubic" },
#       B: { num_flows: 1, protocol: "udp"}, ...
#       "flow_duration": 400
#   }
#
# This helper maintains the following lists, for easy external access to all of the objects
# created in it:
#   * nodes = Dictionary containing all nodes created in the topology, it contains:
#       - senders = List of all sender nodes, stored in lexicographic order. They can be accessed
#         as nodes["senders"][0] for A1 nodes["senders"][1] for B, ..., nodes["senders"][5] for F
#       - receivers = List of all receiver nodes, stored in lexicographic order.
#         They can be accessed as nodes["receivers"][0] for A, nodes["receivers"][1] for B,
#         nodes["receivers"][2] for C, ..., nodes["receivers"][5] for F
#       - routers = List of all routers, stored in left to right order. They can be accessed
#         as nodes["routers"][0] for R1, nodes["routers"][1] for R2, ..., nodes["routers"][4] for R5
#   * network_list = List of all network addresses created and used
#   * num_nodes = Dictionary containing the number of nodes of each type:
#       - senders = Number of sender nodes
#       - receivers = Number of receiver nodes
#       - routers = Number of router nodes
#   * interfaces = Dictionary containing all interfaces created in the topology, it contains:
#       - senders = List of interfaces on the sender nodes,
#          stored following the order of nodes["senders"] in lexicographic order:
#          eths1, eths2, .... eths6
#       - receivers = List of the interfaces of the receiver nodes,
#         stored following the order of nodes["receivers"] in lexicographic order:
#         ethr1, ethr2, .... ethr6
#       - routers = Nested list, where every i-th inner list is the
#         list of all interfaces of the i-th router, stored following the order of nodes["routers"].
#         The interfaces are stored in lexicographic order for each router, i.e.,
#         etr1a, etr1b, etr1c for R1, etr2a, etr2b, etr2c, etr2d, etr2e for R2, ...
#
# The helper contains the following methods to access the nodes and their interfaces:
# Note: The naming conventions are as per the diagram provided below.
#
#   - get_sender(index): returns the sender node at position 'index' in the list of sender nodes.
#     The nodes can be accessed lexicographically, i.e, A is at index 0,
#     B is at index 1, ..., F is at index 5
#
#   - get_receiver(index): returns the receiver node at position 'index',
#     in the list of receiver nodes. The nodes can be accessed lexicographically, i.e,
#     A is at index 0, B is at index 1, ..., F is at index 5
#
#   - get_router(index): returns the router node at position 'index' in the list of router nodes.
#     The nodes can be accessed in the order they are defined in the diagram, i.e, R1 is at index 0,
#     R2 is at index 1, ..., R5 is at index 4
#
#   - get_sender_interfaces(index): returns the interface for the sender at position 'index',
#     the interfaces are stored following the order of sender nodes: eths1, eths2, .... eths6
#
#   - get_receiver_interfaces(index): returns the interface for the receiver at position 'index',
#     the interfaces are stored following the order of receiver nodes: ethr1, ethr2, .... ethr6
#
#   - get_router_interfaces(index):
#     returns a list of all interfaces of the router at position 'index',
#     the router can be accessed in the order they are defined in the diagram,
#     i.e, R1 is at index 0, R2 is at index 1, ..., R5 is at index 4.
#     The returned list contains interfaces of the router in lexicographic order, i.e,
#     etr1a, etr1b, etr1c for R1, etr2a, etr2b, etr2c, etr2d, etr2e for R2, ...
#
# The following is the interfaces for reference:
#   * interfaces["senders"] = [eths1, eths2, .... eths6]
#   * interfaces["receivers"] = [ethr1, ethr2, .... ethr6]
#   * interfaces["routers"] = [[etr1a, etr1b, etr1c],
#     [etr2a, etr2b, etr2c, etr2d, etr2e], [etr3a, etr3b, etr3c, etr3d],
#     [etr4a, etr4b, etr4c, etr4d, etr4e], [etr5a, etr5b, etr5c]]
#
# Note:
# When using set_attributes() to configure link parameters, always specify the qdisc explicitly.
# If omitted, pfifo is set as the default qdisc.
#
# ###############################################################################################
#
#                                Network Topology Diagram

# ###############################################################################################
#
# (s)           (r)           (r)        (r)     (r)      (r)
# A(3)          D(6)          F(2)       A(3)    C(3)     E(6)
#  |             |             |          \      /         |
#  |             |             |           \    /          |
#  |             |             |            \  /           |
#  |             |             |             \/            |
#  R1 ---------- R2 ---------- R3 ---------- R4 ---------- R5
#  |             /\            |             |             |
#  |            /  \           |             |             |
#  |           /    \          |             |             |
#  |          /      \         |             |             |
# D(6)       B(3)      F(2)    C(3)          E(6)          B(3)
# (s)        (s)       (s)     (s)           (s)           (r)

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
# - Sender interfaces are named as 'ethsX', where X is the sender node number
# - Receiver interfaces are named as 'ethrX', where X is the receiver node number
# - Router interfaces are named as 'etrXY', where X is the router number and Y
#   is the interface identifier (a, b, c, ...)
#
#   Note: The interface names shown are for diagrammatic representation only.
#         The code does not assign these names to the interfaces.
#
# Interfaces of Senders:
#   - eths1   <-> Node A(3) (sender) (2001:1::/120) [50 Mbit/s, 4 ms]
#   - eths2   <-> Node B(3) (sender) (2001:2::/120) [50 Mbit/s, 4 ms]
#   - eths3   <-> Node C(3) (sender) (2001:3::/120) [50 Mbit/s, 4 ms]
#   - eths4   <-> Node D(6) (sender) (2001:4::/120) [50 Mbit/s, 4 ms]
#   - eths5   <-> Node E(6) (sender) (2001:5::/120) [50 Mbit/s, 4 ms]
#   - eths6   <-> Node F(2) (sender) (2001:6::/120) [50 Mbit/s, 4 ms]
#
# Interfaces of Receivers:
#   - ethr1   <-> Node A(3) (receiver) (2001:11::/120) [50 Mbit/s, 4 ms]
#   - ethr2   <-> Node B(3) (receiver) (2001:12::/120) [50 Mbit/s, 4 ms]
#   - ethr3   <-> Node C(3) (receiver) (2001:13::/120) [50 Mbit/s, 4 ms]
#   - ethr4   <-> Node D(6) (receiver) (2001:14::/120) [50 Mbit/s, 4 ms]
#   - ethr5   <-> Node E(6) (receiver) (2001:15::/120) [50 Mbit/s, 4 ms]
#   - ethr6   <-> Node F(2) (receiver) (2001:16::/120) [50 Mbit/s, 4 ms]
#
# Interfaces of R1:
#   - etr1a   <-> Node A(3) (sender) [50 Mbit/s, 4 ms]
#   - etr1b   <-> Node D(6) (sender) [50 Mbit/s, 4 ms]
#   - etr1c   <-> R2:etr2c (2001:7::/120)  [50 Mbit/s, 0.167 ms]
#
# Interfaces of R2:
#   - etr2a   <-> Node B(3) (sender) [50 Mbit/s, 4 ms]
#   - etr2b   <-> Node F(2) (sender) [50 Mbit/s, 4 ms]
#   - etr2c   <-> R1:etr1c (2001:7::/120)  [50 Mbit/s, 0.167 ms]
#   - etr2d   <-> R3:etr3b (2001:8::/120)  [150 Mbit/s, 0.167 ms]
#   - etr2e   <-> Node D(6) (receiver) [50 Mbit/s, 4 ms]
#
# Interfaces of R3:
#   - etr3a   <-> Node C(3) (sender) [50 Mbit/s, 4 ms]
#   - etr3b   <-> R2:etr2d   (2001:8::/120) [150 Mbit/s, 0.167 ms]
#   - etr3c   <-> R4:etr4b   (2001:9::/120) [150 Mbit/s, 0.167 ms]
#   - etr3d   <-> Node F(2) (receiver) [50 Mbit/s, 4 ms]
#
# Interfaces of R4:
#   - etr4a   <-> Node E(6) (sender) [50 Mbit/s, 4 ms]
#   - etr4b   <-> R3:etr3c   (2001:9::/120) [150 Mbit/s, 0.167 ms]
#   - etr4c   <-> R5:etr5a   (2001:10::/120) [100 Mbit/s, 0.167 ms]
#   - etr4d   <-> Node A(3) (receiver) [50 Mbit/s, 4 ms]
#   - etr4e   <-> Node C(3) (receiver) [50 Mbit/s, 4 ms]
#
# Interfaces of R5:
#   - etr5a   <-> R4:etr4c   (2001:10::/120) [100 Mbit/s, 0.167 ms]
#   - etr5b   <-> Node B(3) (receiver) [50 Mbit/s, 4 ms]
#   - etr5c   <-> Node E(6) (receiver) [50 Mbit/s, 4 ms]
#
# ###############################################################################################


class Gfc1Helper:
    """
    Helper class to create GFC-1 topology

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

    use_ipv6 : bool
        Flag indicating whether IPv6 addressing is used

    enable_routing_logs : bool
        Flag indicating whether routing logs are enabled

    net_count : int
        Counter to track the current network index while assigning addresses

    Methods
    -------
    __init__(exp, flows=None, use_ipv6=True, enable_routing_logs=False)
        Creates the GFC-1 topology with the given parameters

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

    _configure_links()
        Configures link attributes for all interfaces

    _setup_flows(exp, flows)
        Sets up the flows between senders and receivers based on the provided flow configuration

    """

    def __init__(self, exp, flows=None, use_ipv6=True, enable_routing_logs=False):
        """
        Creates the GFC-1 topology with the given parameters:

        Parameters
        ----------
        exp : Experiment
            An Experiment object that should be created before this helper is used
        flows : dict, optional
            A dictionary specifying the number and the kind of flows that the senders should send,
            along with the duration of the flows
            (default: None, in which case all senders send TCP flows with CUBIC congestion control
             for 300 seconds each)
        use_ipv6 : bool, optional
            A boolean flag indicating whether IPv6 addressing should be used
            (default: True)
        enable_routing_logs : bool, optional
            A boolean flag to enable or disable routing logs
            (default: False)
        """

        if flows is None:
            flows = {}

        self.nodes = {
            "senders": [],
            "receivers": [],
            "routers": [],
        }

        self.use_ipv6 = use_ipv6
        self.enable_routing_logs = enable_routing_logs
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
        config.set_value("routing_suite", "frr")
        config.set_value("routing_logs", self.enable_routing_logs)

    def _create_nodes_and_routers(self):
        """
        Creates sender nodes, receiver nodes, and routers
        """
        self.num_nodes = {
            "senders": 6,
            "receivers": 6,
            "routers": 5,
        }

        # Creating sender and receiver nodes
        self.nodes["senders"] = [
            Node(chr(65 + i)) for i in range(self.num_nodes["senders"])
        ]

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
        if self.use_ipv6:
            count = (
                self.num_nodes["senders"]
                + self.num_nodes["receivers"]
                + self.num_nodes["routers"]
                - 1
            )
            self.network_list = [
                Network(f"2001:{i}::/120") for i in range(1, count + 1)
            ]
        else:
            count = (
                self.num_nodes["senders"]
                + self.num_nodes["receivers"]
                + self.num_nodes["routers"]
                - 1
            )
            self.network_list = [
                Network(f"192.168.{i}.0/24") for i in range(1, count + 1)
            ]

        # Counter to track the current network index while assigning addresses
        self.net_count = 0

    def _connect_senders(self):
        """
        Connects sender nodes to the routers
        """
        # Connecting interface of sender A (eths1) to the interface of router R1 (etr1a)
        [sender_interface, router_interface] = connect(
            self.nodes["senders"][0],
            self.nodes["routers"][0],
            network=self.network_list[self.net_count],
        )
        self.interfaces["senders"].append(sender_interface)
        self.interfaces["routers"][0].append(router_interface)
        self.net_count += 1

        # Connecting interface of sender B (eths2) to the interface of router R2 (etr2a)
        [sender_interface, router_interface] = connect(
            self.nodes["senders"][1],
            self.nodes["routers"][1],
            network=self.network_list[self.net_count],
        )
        self.interfaces["senders"].append(sender_interface)
        self.interfaces["routers"][1].append(router_interface)
        self.net_count += 1

        # Connecting interface of sender C (eths3) to the interface of router R3 (etr3a)
        [sender_interface, router_interface] = connect(
            self.nodes["senders"][2],
            self.nodes["routers"][2],
            network=self.network_list[self.net_count],
        )
        self.interfaces["senders"].append(sender_interface)
        self.interfaces["routers"][2].append(router_interface)
        self.net_count += 1

        # Connecting interface of sender D (eths4) to the interface of router R1 (etr1b)
        [sender_interface, router_interface] = connect(
            self.nodes["senders"][3],
            self.nodes["routers"][0],
            network=self.network_list[self.net_count],
        )
        self.interfaces["senders"].append(sender_interface)
        self.interfaces["routers"][0].append(router_interface)
        self.net_count += 1

        # Connecting interface of sender E (eths5) to the interface of router R4 (etr4a)
        [sender_interface, router_interface] = connect(
            self.nodes["senders"][4],
            self.nodes["routers"][3],
            network=self.network_list[self.net_count],
        )
        self.interfaces["senders"].append(sender_interface)
        self.interfaces["routers"][3].append(router_interface)
        self.net_count += 1

        # Connecting interface of sender F (eths6) to the interface of router R2 (etr2b)
        [sender_interface, router_interface] = connect(
            self.nodes["senders"][5],
            self.nodes["routers"][1],
            network=self.network_list[self.net_count],
        )
        self.interfaces["senders"].append(sender_interface)
        self.interfaces["routers"][1].append(router_interface)
        self.net_count += 1

    def _connect_routers(self):
        """
        Connects routers to each other
        """
        # Connecting interface of router R1 (etr1c) to the interface of router R2 (etr2c)
        [router1_interface, router2_interface] = connect(
            self.nodes["routers"][0],
            self.nodes["routers"][1],
            network=self.network_list[self.net_count],
        )
        self.interfaces["routers"][0].append(router1_interface)
        self.interfaces["routers"][1].append(router2_interface)
        self.net_count += 1

        # Connecting interface of router R2 (etr2d) to the interface of router R3 (etr3b)
        [router2_interface, router3_interface] = connect(
            self.nodes["routers"][1],
            self.nodes["routers"][2],
            network=self.network_list[self.net_count],
        )
        self.interfaces["routers"][1].append(router2_interface)
        self.interfaces["routers"][2].append(router3_interface)
        self.net_count += 1

        # Connecting interface of router R3 (etr3c) to the interface of router R4 (etr4b)
        [router3_interface, router4_interface] = connect(
            self.nodes["routers"][2],
            self.nodes["routers"][3],
            network=self.network_list[self.net_count],
        )
        self.interfaces["routers"][2].append(router3_interface)
        self.interfaces["routers"][3].append(router4_interface)
        self.net_count += 1

        # Connecting interface of router R4 (etr4c) to the interface of router R5 (etr5a)
        [router4_interface, router5_interface] = connect(
            self.nodes["routers"][3],
            self.nodes["routers"][4],
            network=self.network_list[self.net_count],
        )
        self.interfaces["routers"][3].append(router4_interface)
        self.interfaces["routers"][4].append(router5_interface)
        self.net_count += 1

    def _connect_receivers(self):
        """
        Connects receiver nodes to the routers
        """
        # Connecting interface of receiver A (ethr1) to the interface of router R4 (etr4d)
        [receiver_interface, router_interface] = connect(
            self.nodes["receivers"][0],
            self.nodes["routers"][3],
            network=self.network_list[self.net_count],
        )
        self.interfaces["receivers"].append(receiver_interface)
        self.interfaces["routers"][3].append(router_interface)
        self.net_count += 1

        # Connecting interface of receiver B (ethr2) to the interface of router R5 (etr5b)
        [receiver_interface, router_interface] = connect(
            self.nodes["receivers"][1],
            self.nodes["routers"][4],
            network=self.network_list[self.net_count],
        )
        self.interfaces["receivers"].append(receiver_interface)
        self.interfaces["routers"][4].append(router_interface)
        self.net_count += 1

        # Connecting interface of receiver C (ethr3) to the interface of router R4 (etr4e)
        [receiver_interface, router_interface] = connect(
            self.nodes["receivers"][2],
            self.nodes["routers"][3],
            network=self.network_list[self.net_count],
        )
        self.interfaces["receivers"].append(receiver_interface)
        self.interfaces["routers"][3].append(router_interface)
        self.net_count += 1

        # Connecting interface of receiver D (ethr4) to the interface of router R2 (etr2e)
        [receiver_interface, router_interface] = connect(
            self.nodes["receivers"][3],
            self.nodes["routers"][1],
            network=self.network_list[self.net_count],
        )
        self.interfaces["receivers"].append(receiver_interface)
        self.interfaces["routers"][1].append(router_interface)
        self.net_count += 1

        # Connecting interface of receiver E (ethr5) to the interface of router R5 (etr5c)
        [receiver_interface, router_interface] = connect(
            self.nodes["receivers"][4],
            self.nodes["routers"][4],
            network=self.network_list[self.net_count],
        )
        self.interfaces["receivers"].append(receiver_interface)
        self.interfaces["routers"][4].append(router_interface)
        self.net_count += 1

        # Connecting interface of receiver F (ethr6) to the interface of router R3 (etr3d)
        [receiver_interface, router_interface] = connect(
            self.nodes["receivers"][5],
            self.nodes["routers"][2],
            network=self.network_list[self.net_count],
        )
        self.interfaces["receivers"].append(receiver_interface)
        self.interfaces["routers"][2].append(router_interface)
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

        # Using OSPF routing protocol for setting the routes on the routers
        RoutingHelper(
            protocol="ospf", ipv6_routing=self.use_ipv6
        ).populate_routing_tables()

    def _configure_links(self):
        """
        Configures link attributes for all interfaces
        """
        link_bandwidth = "50mbit"
        link_latency = "4ms"
        qdisc = "pfifo"

        # Setting default attributes for interfaces of senders
        for _, iface in enumerate(self.interfaces["senders"]):
            iface.set_attributes(link_bandwidth, link_latency, qdisc)

        # Setting default attributes for interfaces of receivers
        for _, iface in enumerate(self.interfaces["receivers"]):
            iface.set_attributes(link_bandwidth, link_latency)

        # Setting default attributes for interfaces of routers
        for router_interface_list in self.interfaces["routers"]:
            for interface in router_interface_list:
                interface.set_attributes(link_bandwidth, link_latency, qdisc)

        # Setting default attributes for inter-router links
        self.interfaces["routers"][0][2].set_attributes("50mbit", "12ms", qdisc)
        self.interfaces["routers"][1][2].set_attributes("50mbit", "12ms", qdisc)
        self.interfaces["routers"][1][3].set_attributes("150mbit", "12ms", qdisc)
        self.interfaces["routers"][2][1].set_attributes("150mbit", "12ms", qdisc)
        self.interfaces["routers"][2][2].set_attributes("150mbit", "12ms", qdisc)
        self.interfaces["routers"][3][1].set_attributes("150mbit", "12ms", qdisc)
        self.interfaces["routers"][3][2].set_attributes("100mbit", "12ms", qdisc)
        self.interfaces["routers"][4][0].set_attributes("100mbit", "12ms", qdisc)

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
        default_flows = {"A": 3, "B": 3, "C": 3, "D": 6, "E": 6, "F": 2}

        # Adding flows
        for i, (node, value) in enumerate(default_flows.items()):

            num_flows = flows.get(node, {}).get("num_flows", value)
            protocol = flows.get(node, {}).get("protocol", "tcp")
            if protocol == "tcp":
                tcp_type = flows.get(node, {}).get("tcp_type", "cubic")

            # Setting flow duration for all flows
            # The default is 300 seconds, but can be overridden
            flow_duration = flows.get("flow_duration", 300)

            vars()["flow" + str(i + 1)] = Flow(
                self.nodes["senders"][i],
                self.nodes["receivers"][i],
                self.interfaces["receivers"][i].get_address(),
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
