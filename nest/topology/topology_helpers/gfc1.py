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
# The design for this GFC (Generic Fairness Configuration) is derived from the
# test configurations described in:
# Robert J. Simcoe,"Test configurations for fairness and other tests",
# ATM Forum/94-0557, July 1994.

# The network topology consists of 6 sender nodes (A, B, C, D, E, F),
# 6 receiver nodes (A, B, C, D, E, F) and 5 routers (R1, R2, R3, R4, R5).
#
# The customizations provided for the users who use the helper are:
#   * the number of flows between the senders and receivers
#   * the choice of qdiscs and its configurable attributes.
#
# This helper expects three parameters:
#   * exp = An Experiment object that should be created before this helper is used (mandatory)
#   * flows = A dictionary specifying the number and the kind of flows that the senders should send,
#             along with the flow duration (via the key "flow_duration").
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
# - Usable for up to 256 nodes.
#
# If use_ipv6 flag is set to False, the following address type is used: 192.168.i.0/24
#   where i is the flow index (1, 2, 3, ...)
# - Example: 192.168.1.0/24, 192.168.2.0/24, 192.168.3.0/24
# - Each /24 subnet provides 256 addresses (2^8 host bits)
# - Usable for up to 254 nodes (excluding network/broadcast)
#
# If use_dynamic_routing flag is set to True,
#    OSPF routing protocol is used for routing between the routers.
#
# If use_dynamic_routing flag is set to False,
#    static routes are set up between the nodes and routers.
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

    _setup_static_routes(use_ipv6)
        Sets up static routes for all senders, receivers and routers

    _configure_links()
        Configures link attributes for all interfaces

    _setup_flows(exp, flows)
        Sets up the flows between senders and receivers based on the provided flow configuration

    """

    def __init__(self, exp, flows=None, topology_config=None):
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

        self.nodes = {
            "senders": [],
            "receivers": [],
            "routers": [],
        }

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

        # Setting the routing suite and routing logs based on the use_dynamic_routing flag
        if self.topology_config["use_dynamic_routing"]:
            # Using FRR (Free Range Routing) as the routing suite,
            # to be able to use routing protocols like OSPF
            config.set_value("routing_suite", "frr")
            config.set_value(
                "routing_logs", self.topology_config["enable_routing_logs"]
            )

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
            (4, 3),
            (5, 1),
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
            (0, 3),
            (1, 4),
            (2, 3),
            (3, 1),
            (4, 4),
            (5, 2),
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
        Sets up static routes for all senders, receivers and routers

        Sender networks (net indices 1-6):
          net 1  : sA  <-> R1   (sender_router_map index 0)
          net 2  : sB  <-> R2   (sender_router_map index 1)
          net 3  : sC  <-> R3   (sender_router_map index 2)
          net 4  : sD  <-> R1   (sender_router_map index 3)
          net 5  : sE  <-> R4   (sender_router_map index 4)
          net 6  : sF  <-> R2   (sender_router_map index 5)

        Router-router networks (net indices 7-10):
          net 7  : R1  <-> R2
          net 8  : R2  <-> R3
          net 9  : R3  <-> R4
          net 10 : R4  <-> R5

        Receiver networks (net indices 11-16):
          net 11 : rA  <-> R4   (receiver_router_map index 0)
          net 12 : rB  <-> R5   (receiver_router_map index 1)
          net 13 : rC  <-> R4   (receiver_router_map index 2)
          net 14 : rD  <-> R2   (receiver_router_map index 3)
          net 15 : rE  <-> R5   (receiver_router_map index 4)
          net 16 : rF  <-> R3   (receiver_router_map index 5)
        """

        def net(index):
            """Returns the network address string for the given 1-based network index."""
            if use_ipv6:
                return f"2001:{index}::/120"
            return f"192.168.{index}.0/24"

        # Convenience aliases for router interface lists
        r_1 = self.interfaces["routers"][0]  # [0:→sA,  1:→sD,  2:→R2]
        r_2 = self.interfaces["routers"][1]  # [0:→sB,  1:→sF,  2:→R1,  3:→R3, 4:→rD]
        r_3 = self.interfaces["routers"][2]  # [0:→sC,  1:→R2,  2:→R4,  3:→rF]
        r_4 = self.interfaces["routers"][3]  # [0:→sE,  1:→R3,  2:→R5,  3:→rA, 4:→rC]
        r_5 = self.interfaces["routers"][4]  # [0:→R4,  1:→rB,  2:→rE]

        # Attach Routes to R1
        # Directly attached sender networks — use local interfaces
        self.nodes["routers"][0].add_route(net(1), r_1[0])  # sA  via etr1a
        self.nodes["routers"][0].add_route(net(4), r_1[1])  # sD  via etr1b
        # All other networks (sB, sC, sF, sE, all receivers) go via R2
        for idx in [2, 3, 5, 6, 11, 12, 13, 14, 15, 16]:
            self.nodes["routers"][0].add_route(net(idx), r_1[2])

        # Attach Routes to R2
        # Directly attached sender networks — use local interfaces
        self.nodes["routers"][1].add_route(net(2), r_2[0])  # sB  via etr2a
        self.nodes["routers"][1].add_route(net(6), r_2[1])  # sF  via etr2b
        # Directly attached receiver network — use local interface
        self.nodes["routers"][1].add_route(net(14), r_2[4])  # rD  via etr2e
        # sA, sD are behind R1 — go back via R1
        for idx in [1, 4]:
            self.nodes["routers"][1].add_route(net(idx), r_2[2])
        # sC, sE and receivers rA, rB, rC, rE, rF are ahead — go forward via R3
        for idx in [3, 5, 11, 12, 13, 15, 16]:
            self.nodes["routers"][1].add_route(net(idx), r_2[3])

        # Attach Routes to R3
        # Directly attached sender network — use local interface
        self.nodes["routers"][2].add_route(net(3), r_3[0])  # sC  via etr3a
        # Directly attached receiver network — use local interface
        self.nodes["routers"][2].add_route(net(16), r_3[3])  # rF  via etr3d
        # sA, sB, sD, sF, rD are behind R2 — go back via R2
        for idx in [1, 2, 4, 6, 14]:
            self.nodes["routers"][2].add_route(net(idx), r_3[1])
        # sE and receivers rA, rB, rC, rE are ahead — go forward via R4
        for idx in [5, 11, 12, 13, 15]:
            self.nodes["routers"][2].add_route(net(idx), r_3[2])

        # Attach Routes to R4
        # Directly attached sender network — use local interface
        self.nodes["routers"][3].add_route(net(5), r_4[0])  # sE  via etr4a
        # Directly attached receiver networks — use local interfaces
        self.nodes["routers"][3].add_route(net(11), r_4[3])  # rA  via etr4d
        self.nodes["routers"][3].add_route(net(13), r_4[4])  # rC  via etr4e
        # All sender networks (except sE) are behind R3 — go back via R3
        for idx in [1, 2, 3, 4, 6]:
            self.nodes["routers"][3].add_route(net(idx), r_4[1])
        # rD (at R2) and rF (at R3) are also behind R3
        for idx in [14, 16]:
            self.nodes["routers"][3].add_route(net(idx), r_4[1])
        # rB, rE are ahead at R5 — go forward via R5
        for idx in [12, 15]:
            self.nodes["routers"][3].add_route(net(idx), r_4[2])

        # Attach Routes to R5
        # Directly attached receiver networks — use local interfaces
        self.nodes["routers"][4].add_route(net(12), r_5[1])  # rB  via etr5b
        self.nodes["routers"][4].add_route(net(15), r_5[2])  # rE  via etr5c
        # Everything else (all senders, rA, rC, rD, rF) is behind R4
        for idx in [1, 2, 3, 4, 5, 6, 11, 13, 14, 16]:
            self.nodes["routers"][4].add_route(net(idx), r_5[0])

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
            (0, 2, "50mbit", "12ms"),
            (1, 2, "50mbit", "12ms"),
            (1, 3, "150mbit", "12ms"),
            (2, 1, "150mbit", "12ms"),
            (2, 2, "150mbit", "12ms"),
            (3, 1, "150mbit", "12ms"),
            (3, 2, "100mbit", "12ms"),
            (4, 0, "100mbit", "12ms"),
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
