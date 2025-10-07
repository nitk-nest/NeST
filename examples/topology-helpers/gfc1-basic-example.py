# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""Example on using the Gfc1Helper class with default configuration"""

########################
# SHOULD BE RUN AS ROOT
########################
from nest.experiment import Experiment
from nest.topology.topology_helpers.gfc1 import Gfc1Helper

# This program demonstrates how to use the Gfc1Helper class to create a
# GFC-1 topology with default configuration.
#
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
# The example uses the getter method provided by the helper to access the router interfaces
# Note: The naming conventions are as per the diagram provided below.
#   - get_router_interfaces(index):
#     returns a list of all interfaces of the router at position 'index',
#     the router can be accessed in the order they are defined in the diagram,
#     i.e, R1 is at index 0, R2 is at index 1, ..., R5 is at index 4.
#     The returned list contains interfaces of the router in lexicographic order, i.e,
#     etr1a, etr1b, etr1c for R1, etr2a, etr2b, etr2c, etr2d, etr2e for R2, ...
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
# - IPv6 addressing is used
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

# Set up an Experiment. This API takes the name of the experiment as a string.
# The name of the experiment is used to create a directory with the same name,
# where all the results and logs of the experiment are stored.
exp = Experiment("gfc1-basic-example")

# Creates the GFC-1 topology
topology = Gfc1Helper(exp)

# Specify the interfaces at which we need to collect qdisc stats.
# Enable collection of stats for default ('pfifo') qdisc installed on the third interface of R1
# (etr1c), connecting `R1` to `R2`.
exp.require_qdisc_stats(topology.get_router_interface(0, 2))

# Enable collection of stats for default qdisc installed on the fourth interface of R2 (etr2d),
# connecting `R2` to `R3`.
exp.require_qdisc_stats(topology.get_router_interface(1, 3))

# Enable collection of stats for default qdisc installed on the third interface of R3 (etr3c),
# connecting `R3` to `R4`.
exp.require_qdisc_stats(topology.get_router_interface(2, 2))

# Enable collection of stats for default qdisc installed on the third interface of R4 (etr4c),
# connecting `R4` to `R5`.
exp.require_qdisc_stats(topology.get_router_interface(3, 2))

# Run the experiment
exp.run()
