# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""Example for using the Gfc1Helper class with custom configuration"""

########################
# SHOULD BE RUN AS ROOT
########################
from nest.experiment import Experiment
from nest.topology.topology_helpers.gfc1 import Gfc1Helper

# This program demonstrates how to use the Gfc1Helper class to create a
# GFC-1 topology with a few customizations listed below:
#
# 1) customized number of flows and type of flow between a given sender and a receiver node
# 2) customizing the flow duration
# 3) customizing the qdisc and its parameters at the router interfaces
# 4) configuring attributes at interfaces.
# 5) setting use_ipv6 flag to False, thus enabling IPv4 addresses to be used
# 6) setting enable_routing_logs to True to enable routing logs
#
# The network topology consists of 6 sender nodes (A, B, C, D, E, F),
# 6 receiver nodes (A, B, C, D, E, F) and 5 routers (R1, R2, R3, R4, R5).
#
# This helper expects four parameters:
#   * exp = An Experiment object that should be created before this helper is used (mandatory)
#   * flows = A dictionary specifying the number and the kind of flows that the senders should send,
#             along with the duration of the flows (via the key "flow_duration")
#     (optional; if not provided,
#     all senders send TCP flows with cubic congestion control for 300 seconds each)
#   * use_ipv6: A boolean flag indicating whether IPv6 addressing should be used (default: True).
#     (optional; if not provided, IPv6 addresses will be used by default,
#                and if set to False, IPv4 addresses are used)
#   * enable_routing_logs: A boolean flag to enable or disable routing logs (default: False).
#     (optional; if not provided, routing logs are disabled by default)
#
# Example of flows dictionary:
#   flows = {
#       A1: { num_flows: 1, protocol: "tcp", tcp_type: "cubic" },
#       A2: { num_flows: 1, protocol: "tcp", tcp_type: "cubic" },
#       B1: { num_flows: 1, protocol: "udp"}, ...
#       "flow_duration": 400,
#   }
#
# The helper contains the following methods to access the nodes and their interfaces:
# Note: The naming conventions are as per the diagram provided below.
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
# The following are the interfaces for reference:
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
#
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
#
# ===========================
# Network Topology Interfaces
# ===========================
# Flow Conventions:
# - All flows move from left to right
# - (3) indicates 3 parallel flows
# - (s) denotes a sender node
# - (r) denotes a receiver node
# - IPv4 addressing is used
#
# Naming Conventions:
# - Sender interfaces are named as 'ethsX' where X is the sender node number
# - Receiver interfaces are named as 'ethrX' where X is the receiver node number
# - Router interfaces are named as 'etrXY', where X is the router number and,
#   Y is the interface identifier (a,b,c...)
#
#  Note: The interface names shown are for diagrammatic representation only.
#        The code does not assign these names to the interfaces.
#
# Interfaces of Senders:
#   - eths1   <-> Node A(3) (sender) (192.168.1.0/24)
#   - eths2   <-> Node B(3) (sender) (192.168.2.0/24)
#   - eths3   <-> Node C(3) (sender) (192.168.3.0/24)
#   - eths4   <-> Node D(6) (sender) (192.168.4.0/24)
#   - eths5   <-> Node E(6) (sender) (192.168.5.0/24)
#   - eths6   <-> Node F(2) (sender) (192.168.6.0/24)
#
# Interfaces of Receivers:
#   - ethr1   <-> Node A(3) (receiver) (192.168.11.0/24)
#   - ethr2   <-> Node B(3) (receiver) (192.168.12.0/24)
#   - ethr3   <-> Node C(3) (receiver) (192.168.13.0/24)
#   - ethr4   <-> Node D(6) (receiver) (192.168.14.0/24)
#   - ethr3   <-> Node E(6) (receiver) (192.168.15.0/24)
#   - ethr6   <-> Node F(2) (receiver) (192.168.16.0/24)
#
# Interfaces of R1:
#   - etr1a   <-> Node A(3) (sender)
#   - etr1b   <-> Node D(6) (sender)
#   - etr1c   <-> R2:etr2c (192.168.7.0/24)  [50 Mbit/s, 0.167 ms]
#
# Interfaces of R2:
#   - etr2a   <-> Node B(3) (sender)
#   - etr2b   <-> Node F(2) (sender)
#   - etr2c   <-> R1:etr1c (192.168.7.0/24)  [50 Mbit/s, 0.167 ms]
#   - etr2d   <-> R3:etr3b (192.168.8.0/24)  [150 Mbit/s, 0.167 ms]
#   - etr2e   <-> Node D(6) (receiver)
#
# Interfaces of R3:
#   - etr3a   <-> Node C(3) (sender)
#   - etr3b   <-> R2:etr2d   (192.168.8.0/24) [150 Mbit/s, 0.167 ms]
#   - etr3c   <-> R4:etr4b   (192.168.9.0/24) [150 Mbit/s, 0.167 ms]
#   - etr3d   <-> Node F(2) (receiver)
#
# Interfaces of R4:
#   - etr4a   <-> Node E(6) (sender)
#   - etr4b   <-> R3:etr3c   (192.168.9.0/24) [150 Mbit/s, 0.167 ms]
#   - etr4c   <-> R5:etr5a   (192.168.10.0/24) [100 Mbit/s, 0.167 ms]
#   - etr4d   <-> Node A(3) (receiver)
#   - etr4e   <-> Node C(3) (receiver)
#
# Interfaces of R5:
#   - etr5a   <-> R4:etr4c   (192.168.10.0/24) [100 Mbit/s, 0.167 ms]
#   - etr5b   <-> Node B(3) (receiver)
#   - etr5c  <-> Node E(6) (receiver)
#
# ###############################################################################################

# Define the flows between the sender and receiver nodes.
# We define 3 types of flows:
# 1) 2 TCP flows from A to A using cubic congestion control algorithm,
# 2) 1 UDP flow from B to B,
# 3) 4 UDP flows from C to C.
# The keys of the `flows` dictionary are the sender nodes.
# The values are dictionaries with the following keys:
# - "num_flows": number of flows from a sender node to the corresponding receiver node,
# - "protocol":  the protocol of the flow : "tcp" or "udp",
# - "tcp_type": the congestion control algorithm to be used for TCP flows.
#               This key is ignored for non-TCP flows.
#               The default value is "cubic" if not specified.
#               Other supported values are "bbr", "reno", "vegas" etc.
# The flow duration can be specified via the key "flow_duration"
# It is set to 150 seconds in this example.

flows = {
    "A": {"num_flows": 2, "protocol": "tcp", "tcp_type": "cubic"},
    "B": {"num_flows": 1, "protocol": "udp"},
    "C": {"num_flows": 4, "protocol": "udp"},
    "flow_duration": 150,  # duration of each flow in seconds
}

# Set up an Experiment. This API takes the name of the experiment as a string.
# The name of the experiment is used to create a directory with the same name,
# where all the results and logs of the experiment are stored.
exp = Experiment("gfc1-custom-config")

# Creates the GFC-1 topology
# use_ipv6 flag is set to False to enable IPv4 addressing
# enable_routing_logs is set to True to enable routing logs
topology = Gfc1Helper(exp, flows, use_ipv6=False, enable_routing_logs=True)

# Configure the parameters of `fq_codel` qdisc.
# This is an example of how to set a custom qdisc and its parameters
# at an interface of a router.
qdisc = "fq_codel"
fq_codel_parameters = {"limit": "100"}  # set the queue capacity to 100 packets

# `fq_codel` qdisc is configured with a queue limit of 100 packets,
# at the interface `etr1c` of router `R1` on the link from `R1` to `R2`.
topology.get_router_interface(0, -1).set_attributes(
    "20mbit", "10ms", qdisc, **fq_codel_parameters
)

# `fq_codel` qdisc is configured with a queue limit of 100 packets,
# at the interface `etr1c` of router `R3`on the link from `R3` to `R4`.
topology.get_router_interface(2, -2).set_attributes(
    "20mbit", "10ms", qdisc, **fq_codel_parameters
)

# Custom link attributes are set at the sender interfaces.
# Set link attributes for eths1 to custom values.
topology.get_sender_interface(0).set_attributes("10mbit", "10ms", "pfifo")
# Set link attributes for eths2 to custom values.
topology.get_sender_interface(1).set_attributes("10mbit", "10ms", "pfifo")

# Specify the interfaces at which we need to collect qdisc stats.
# Enable collection of stats for `fq_codel` qdisc installed on the third interface of R1
# (etr1c), connecting `R1` to `R2`.
exp.require_qdisc_stats(topology.get_router_interface(0, 2))

# Enable collection of stats for default ('pfifo') qdisc installed on the fourth interface of R2
# (etr2d), connecting `R2` to `R3`.
exp.require_qdisc_stats(topology.get_router_interface(1, 3))

# Enable collection of stats for `fq_codel` qdisc installed on the third interface of R3
# (etr3c), connecting `R3` to `R4`.
exp.require_qdisc_stats(topology.get_router_interface(2, 2))

# Enable collection of stats for default ('pfifo') qdisc installed on the third interface of R4
# (etr4c), connecting `R4` to `R5`.
exp.require_qdisc_stats(topology.get_router_interface(3, 2))

# Run the experiment
exp.run()
