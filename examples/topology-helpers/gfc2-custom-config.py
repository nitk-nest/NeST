# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""Example for using the Gfc2Helper class with custom configuration"""

########################
# SHOULD BE RUN AS ROOT
########################
from nest.experiment import Experiment
from nest.topology.topology_helpers.gfc2 import Gfc2Helper

# This program demonstrates how to use the Gfc2Helper class to create a
# GFC-2 topology with a few customizations listed below:
#
# 1) customized number of flows and type of flow between a given sender and a receiver node
# 2) customizing the flow duration
# 3) customizing the qdisc and its parameters at the router interfaces
# 4) configuring attributes at interfaces.
# 5) setting use_ipv6 flag to False, thus enabling IPv4 addresses to be used
# 6) setting enable_routing_logs to True to enable routing logs
#
# The network considered in this example has:
# 12 sender nodes (A1, A2, A3, B1, B2, B3, C, D, E, F, G, H),
# 8 receiver nodes (A, B, C, D, E, F, G, H) and
# 7 routers (R1, R2, R3, R4, R5, R6, R7).
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
# The helper provides the following methods to access the interfaces of the nodes:
# Note: The naming conventions are as per the diagram provided below.
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
# ################################################################################################
#
#                                  Network Topology Diagram
#
# ################################################################################################
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
#   - eths1  <-> Node A1(1)  (sender) (192.168.1.0/24) [50 Mbit/s, 4 ms]
#   - eths2  <-> Node A2(1)  (sender) (192.168.2.0/24) [50 Mbit/s, 4 ms]
#   - eths3  <-> Node A3(1)  (sender) (192.168.3.0/24) [50 Mbit/s, 4 ms]
#   - eths4  <-> Node B1(1)  (sender) (192.168.4.0/24) [50 Mbit/s, 4 ms]
#   - eths5  <-> Node B2(1)  (sender) (192.168.5.0/24) [50 Mbit/s, 4 ms]
#   - eths6  <-> Node B3(1)  (sender) (192.168.6.0/24) [50 Mbit/s, 4 ms]
#   - eths7  <-> Node C(3)   (sender) (192.168.7.0/24) [50 Mbit/s, 4 ms]
#   - eths8  <-> Node D(1)   (sender) (192.168.8.0/24) [50 Mbit/s, 4 ms]
#   - eths9  <-> Node E(2)   (sender) (192.168.9.0/24) [50 Mbit/s, 4 ms]
#   - eths10 <-> Node F(1)   (sender) (192.168.10.0/24) [50 Mbit/s, 4 ms]
#   - eths11 <-> Node G(7)   (sender) (192.168.11.0/24) [50 Mbit/s, 4 ms]
#   - eths12 <-> Node H(2)   (sender) (192.168.12.0/24) [50 Mbit/s, 4 ms]
#
# Interfaces of Receivers:
#   - ethr1  <-> Node A(3)   (receiver) (192.168.19.0/24) [50 Mbit/s, 4 ms]
#   - ethr2  <-> Node B(3)   (receiver) (192.168.20.0/24) [50 Mbit/s, 4 ms]
#   - ethr3  <-> Node C(3)   (receiver) (192.168.21.0/24) [50 Mbit/s, 4 ms]
#   - ethr4  <-> Node D(1)   (receiver) (192.168.22.0/24) [50 Mbit/s, 4 ms]
#   - ethr5  <-> Node E(2)   (receiver) (192.168.23.0/24) [50 Mbit/s, 4 ms]
#   - ethr6  <-> Node F(1)   (receiver) (192.168.24.0/24) [50 Mbit/s, 4 ms]
#   - ethr7  <-> Node G(7)   (receiver) (192.168.25.0/24) [50 Mbit/s, 4 ms]
#   - ethr8  <-> Node H(2)   (receiver) (192.168.26.0/24) [50 Mbit/s, 4 ms]
#
# Interfaces of R1:
# - etr1a <-> Node A1(1) (sender) [50 Mbit/s, 4 ms]
# - etr1b <-> Node B1(1) (sender) [50 Mbit/s, 4 ms]
# - etr1c <-> Node D(1)  (sender) [50 Mbit/s, 4 ms]
# - etr1d <-> R2:etr2d   (192.168.13.0/24) [50 Mbit/s, 13.33 ms]
#
# Interfaces of R2:
# - etr2a <-> Node A2(1) (sender) [50 Mbit/s, 4 ms]
# - etr2b <-> Node B2(1) (sender) [50 Mbit/s, 4 ms]
# - etr2c <-> Node E(2)  (sender) [50 Mbit/s, 4 ms]
# - etr2d <-> R1:etr1d   (192.168.13.0/24) [50 Mbit/s, 13.33 ms]
# - etr2e <-> R3:etr3c   (192.168.14.0/24) [100 Mbit/s, 6.67 ms]
# - etr2f <-> Node D(1)  (receiver) [50 Mbit/s, 4 ms]
#
# Interfaces of R3:
# - etr3a <-> Node A3(1) (sender) [50 Mbit/s, 4 ms]
# - etr3b <-> Node F(1)  (sender) [50 Mbit/s, 4 ms]
# - etr3c <-> R2:etr2e (192.168.14.0/24) [100 Mbit/s, 6.67 ms]
# - etr3d <-> R4:etr4c (192.168.15.0/24) [50 Mbit/s, 3.33 ms]
# - etr3e <-> Node E(2)  (receiver) [50 Mbit/s, 4 ms]
#
# Interfaces of R4:
# - etr4a <-> Node B3(1) (sender) [50 Mbit/s, 4 ms]
# - etr4b <-> Node H(2)  (sender) [50 Mbit/s, 4 ms]
# - etr4c <-> R3:etr3d (192.168.15.0/24) [50 Mbit/s, 3.33 ms]
# - etr4d <-> R5:etr5b (192.168.16.0/24) [150 Mbit/s, 3.33 ms]
# - etr4e <-> Node F(1)  (receiver) [50 Mbit/s, 4 ms]
#
# Interfaces of R5:
# - etr5a <-> Node C(3) (sender) [50 Mbit/s, 4 ms]
# - etr5b <-> R4:etr4d (192.168.16.0/24) [150 Mbit/s, 3.33 ms]
# - etr5c <-> R6:etr6b (192.168.17.0/24) [150 Mbit/s, 3.33 ms]
# - etr5d <-> Node H(2)  (receiver) [50 Mbit/s, 4 ms]
#
# Interfaces of R6:
# - etr6a <-> Node G(7) (sender) [50 Mbit/s, 4 ms]
# - etr6b <-> R5:etr5c (192.168.17.0/24) [150 Mbit/s, 3.33 ms]
# - etr6c <-> R7:etr7a (192.168.18.0/24) [50 Mbit/s, 6.67 ms]
# - etr6d <-> Node A(3)  (receiver) [50 Mbit/s, 4 ms]
# - etr6e <-> Node C(3)  (receiver) [50 Mbit/s, 4 ms]
#
# Interfaces of R7:
# - etr7a <-> R6:etr6c (192.168.18.0/24) [50 Mbit/s, 6.67 ms]
# - etr7b <-> Node B(3)  (receiver) [50 Mbit/s, 4 ms]
# - etr7c <-> Node G(7)  (receiver) [50 Mbit/s, 4 ms]
#
# #################################################################################################

# Define the flows between the sender and receiver nodes
# We define 4 types of flows:
# 1) 2 TCP flows from A1 to A using cubic congestion control algorithm,
# 2) 3 TCP flows from A2 to A using new reno congestion control algorithm,
# 3) 4 UDP flows from C to C
# 4) 5 UDP flows from F to F
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
    "A1": {"num_flows": 2, "protocol": "tcp", "tcp_type": "cubic"},
    "A2": {"num_flows": 3, "protocol": "tcp", "tcp_type": "reno"},
    "C": {"num_flows": 4, "protocol": "udp"},
    "F": {"num_flows": 5, "protocol": "udp"},
    "flow_duration": 150,  # duration of each flow in seconds
}

# Set up an Experiment. This API takes the name of the experiment as a string.
# The name of the experiment is used to create a directory with the same name,
# where all the results and logs of the experiment are stored.
exp = Experiment("gfc2-custom-config")

# Creates the above GFC2 topology
# use_ipv6 flag is set to False to enable IPv4 addressing
# enable_routing_logs is set to True to enable routing logs
topology = Gfc2Helper(exp, flows, use_ipv6=False, enable_routing_logs=True)

# Configure the parameters of `fq_codel` qdisc.
# This is an example of how to set a custom qdisc and its parameters
qdisc = "fq_codel"
fq_codel_parameters = {"limit": "100"}  # set the queue capacity to 100 packets

# `fq_codel` qdisc is configured with a queue limit of 100 packets,
# at the interface `etr1c` of router `R1` on the link from `R1` to `R2`.
topology.get_router_interface(0, 3).set_attributes(
    "20mbit", "10ms", qdisc, **fq_codel_parameters
)

# `fq_codel` qdisc is configured with a queue limit of 100 packets,
# at the interface `etr1c` of router `r3`on the link from `R3` to `R4`.
topology.get_router_interface(2, 3).set_attributes(
    "20mbit", "10ms", qdisc, **fq_codel_parameters
)

# Custom link attributes are set at the sender interfaces.
# Set link attributes for eths1 to custom values.
topology.get_sender_interface(0).set_attributes("10mbit", "10ms", "pfifo")
# Set link attributes for eths2 to custom values.
topology.get_sender_interface(1).set_attributes("10mbit", "10ms", "pfifo")

# Specify the interfaces at which qdisc stats should be collected.
# Enable collection of stats for `fq_codel` qdisc installed on the third interface of R1
# (etr1c), connecting `R1` to `R2`.
exp.require_qdisc_stats(topology.get_router_interface(0, 3))

# Enable collection of stats for default ('pfifo') qdisc installed on the fourth interface of R2
# (etr2d), connecting `R2` to `R3`.
exp.require_qdisc_stats(topology.get_router_interface(1, 4))

# Enable collection of stats for `fq_codel` qdisc installed on the third interface of R3
# (etr3c), connecting `R3` to `R4`.
exp.require_qdisc_stats(topology.get_router_interface(2, 3))

# Enable collection of stats for default ('pfifo') qdisc installed on the third interface of R4
# (etr4c), connecting `R4` to `R5`.
exp.require_qdisc_stats(topology.get_router_interface(3, 3))

# Enable collection of stats for default ('pfifo') qdisc installed on the third interface of R5
# (etr5c) interface, connecting `R5` to `R6`.
exp.require_qdisc_stats(topology.get_router_interface(4, 2))

# Enable collection of stats for default ('pfifo') qdisc installed on the third interface of R6
# (etr6c) interface, connecting `R6` to `R7`.
exp.require_qdisc_stats(topology.get_router_interface(5, 2))

# Run the experiment
exp.run()
