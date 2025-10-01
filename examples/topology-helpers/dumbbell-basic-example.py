# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""Example on using the DumbbellHelper class with default configuration"""

########################
# SHOULD BE RUN AS ROOT
########################
from nest.experiment import Experiment, Flow
from nest.topology.topology_helpers.dumbbell import DumbbellHelper

# This program demonstrates how to use the DumbbellHelper class to create a
# dumbbell topology with default configuration.

# A dumbbell topology consists of two sets of nodes connected to a router each, and these
# two routers can be connected to each other directly or through multiple other routers
# in the same path linearly. The nodes connected to the left-most router are called the left
# nodes, while those connected to the right-most router are called as the right side nodes.
#
# The network considered in this example has 3 left side nodes
# (lh1, lh2, lh3), 4 right side nodes (rh1, rh2, rh3, rh4) and 2 routers
# (r1, r2; in the middle section of the dumbbell).
#
# The following are the flows configured in this example:
#   * One TCP flow from lh1 to rh1, from the 0th second to the 200th second
#   * One TCP flow from lh2 to rh2, from the 0th second to the 200th second
#   * One TCP flow from lh3 to rh3, from the 0th second to the 100th secondS
#   * One UDP flow from lh3 to rh4, from the 100th second to the 200th second
#
# The links connecting left or right side nodes to the routers are edge links.
# The link between the routers r1 <--> r2 is the bottleneck link with
# lesser bandwidth and higher propagation delay.
#
# This example uses the default settings of the dumbbell helper, namely
# the pfifo qdisc, 10mbit as the bandwidth and 4ms as the delay for
# all of the interfaces.
#
################################################################################
#                              Network Topology                                #
#                                                                              #
#    <- 10mbit, 4ms ->                                    <- 10mbit, 4ms ->    #
# lh1 -------------------|                            |------------------- rh1 #
#           TCP          |                            |         TCP            #
#                        |                            |   <- 10mbit, 4ms ->    #
#                        |                            |------------------- rh2 #
#    <- 10mbit, 4ms ->   |      <- 10mbit, 4ms ->     |         TCP            #
# lh2 -------------------- r1 ---------------------- r2                        #
#           TCP          |                            |   <- 10mbit, 4ms ->    #
#                        |                            |------------------- rh3 #
#                        |                            |         TCP            #
#    <- 10mbit, 4ms ->   |                            |   <- 10mbit, 4ms ->    #
# lh3 -------------------|                            |------------------- rh4 #
#  1 TCP flow, 1 UDP flow                                       UDP            #
#                                                                              #
################################################################################

# Create a dumbbell topology with 3 left side nodes, 4 right side nodes and 2 routers
topology = DumbbellHelper({"left": 3, "right": 4, "routers": 2})

# Set up an Experiment. This API takes the name of the experiment as a string.
exp = Experiment("dumbbell-basic-example")

# Configure the required flows
# One TCP flow from lh1 to rh1, from the 0th second to the 200th second
flow1 = Flow(
    topology.get_left_node(0),
    topology.get_right_node(0),
    topology.get_right_interface(0).get_address(),
    0,
    200,
    1,
)
exp.add_tcp_flow(flow1)

# One TCP flow from lh2 to rh2, from the 0th second to the 200th second
flow2 = Flow(
    topology.get_left_node(1),
    topology.get_right_node(1),
    topology.get_right_interface(1).get_address(),
    0,
    200,
    1,
)
exp.add_tcp_flow(flow2)

# One TCP flow from lh3 to rh3, from the 0th second to the 100th second
flow3 = Flow(
    topology.get_left_node(2),
    topology.get_right_node(2),
    topology.get_right_interface(2).get_address(),
    0,
    100,
    1,
)
exp.add_tcp_flow(flow3)

# One UDP flow from lh3 to rh4, from the 100th second to the 200th second
flow4 = Flow(
    topology.get_left_node(2),
    topology.get_right_node(3),
    topology.get_right_interface(3).get_address(),
    100,
    200,
    1,
)
exp.add_udp_flow(flow4)

# Enable collection of stats for `pfifo` qdisc installed on
# `etr1d` interface, connecting `r1` to `r2`.
exp.require_qdisc_stats(topology.get_router_interface(0, -1))

# Run the experiment
exp.run()
