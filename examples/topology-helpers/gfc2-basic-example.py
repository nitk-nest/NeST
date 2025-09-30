# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2026 NITK Surathkal

"""Example on using the Gfc2Helper class with default configuration"""

########################
# SHOULD BE RUN AS ROOT
########################
from nest.experiment import Experiment
from nest.topology.topology_helpers.gfc2 import Gfc2Helper

# This program demonstrates how to use the Gfc2Helper class to create a
# GFC-2 topology with default configuration.
#
# The network topology consists of 12 sender nodes
# (A1, A2, A3, B1, B2, B3, C, D, E, F, G, H), 8 receiver nodes
# (A, B, C, D, E, F, G, H) and 7 routers (R1, R2, R3, R4, R5, R6, R7).
#
# The customizations provided for the users who use the helper are:
#   * the number of flows between the senders and receivers
#   * the choice of qdiscs and its configurable attributes.
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
# The example uses the getter method provided by the helper to access the router interfaces
# Note: The naming conventions are as per the diagram provided below.
#   - get_router_interfaces(index):
#     returns a list of all interfaces of the router at position 'index',
#     the router can be accessed in the order they are defined in the diagram,
#     i.e, R1 is at index 0, R2 is at index 1, ..., R7 is at index 6.
#     The returned list contains interfaces of the router in lexicographic order, i.e,
#     etr1a, etr1b, etr1c, etr1d for R1, etr2a, etr2b, etr2c, etr2d, etr2e, etr2f for R2, ...
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
#
# ===========================
# Network Topology Interfaces
# ===========================
# Flow Conventions:
# - All flows move from left to right
# - (3) indicates 3 parallel flows
# - (s) denotes a sender node
# - (r) denotes a receiver node
# - IPv6 addressing is used
#
# Naming Conventions:
# - Sender interfaces are named as 'ethsX' where X is the sender node number
# - Receiver interfaces are named as 'ethrX' where X is the receiver node number
# - Router interfaces are named as 'etrXY', where X is the router number and Y
#   the interface identifier (a, b, c, ...)
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

# Set up an Experiment. This API takes the name of the experiment as a string.
# The name of the experiment is used to create a directory with the same name,
# where all the results and logs of the experiment are stored.
exp = Experiment("gfc2-basic-example")

# Creates the GFC-2 topology
topology = Gfc2Helper(exp)

# Specify the interfaces at which we need to collect qdisc stats.
# Enable collection of stats for default ('pfifo') qdisc installed on the fourth interface
# of R1 (etr1d), connecting `R1` to `R2`.
exp.require_qdisc_stats(topology.get_router_interface(0, 3))

# Enable collection of stats for default ('pfifo') qdisc installed on the fifth interface
# of R2 (etr2e), connecting `R2` to `R3`.
exp.require_qdisc_stats(topology.get_router_interface(1, 4))

# Enable collection of stats for default ('pfifo') qdisc installed on the fourth interface
# of R3 (etr3d), connecting `R3` to `R4`.
exp.require_qdisc_stats(topology.get_router_interface(2, 3))

# Enable collection of stats for default ('pfifo') qdisc installed on the fourth interface
# of R4 (etr4d), connecting `R4` to `R5`.
exp.require_qdisc_stats(topology.get_router_interface(3, 3))

# Enable collection of stats for default ('pfifo') qdisc installed on the third interface
# of R5 (etr5c), connecting `R5` to `R6`.
exp.require_qdisc_stats(topology.get_router_interface(4, 2))

# Enable collection of stats for default ('pfifo') qdisc installed on the third interface
# of R6 (etr6c), connecting `R6` to `R7`.
exp.require_qdisc_stats(topology.get_router_interface(5, 2))

# Run the experiment
exp.run()
