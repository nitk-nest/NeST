# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""Example on using the DumbbellHelper class with custom configuration"""

########################
# SHOULD BE RUN AS ROOT
########################
from nest.experiment import Experiment, Flow
from nest.topology.topology_helpers.dumbbell import DumbbellHelper

# This program demonstrates how to use the DumbbellHelper class to create a
# dumbbell topology, and how its various components (like interfaces of nodes
# and routers) can be accessed and modified.
#
# This example builds upon dumbbell-basic-example.py, where:
#   * The network considered had 3 left side nodes (lh1, lh2, lh3),
#     4 right side nodes (rh1, rh2, rh3, rh4) and 2 routers (r1, r2;
#     in the middle section of the dumbbell).
#   * The flows configured were:
#      ** One TCP flow from lh1 to rh1, from the 0th second to the 200th second
#      ** One TCP flow from lh2 to rh2, from the 0th second to the 200th second
#      ** One TCP flow from lh3 to rh3, from the 0th second to the 100th second
#      ** One UDP flow from lh3 to rh4, from the 100th second to the 200th second
#
# This example shows how the default configurations set by the DumbbellHelper
# class can be modified.
#
# The following modifications have been shown in this file:
#   * The address family used is IPv4, instead of the default setting of IPv6.
#   * FRR logging has been enabled (disabled by default).
#   * The qdisc on the left-most router (on the interface towards r2) has been changed
#     from the default pfifo setting to the fq-codel qdisc (with a queue capacity
#     of 100 packets, a target queue delay of 2ms, an interval of 24ms
#     and with ECN marking enabled).
#   * The bandwidth and delay of the interface of r1 towards r2 (same as above)
#     have been changed from the default values of (10mbit, 4ms)
#     to (20mbit, 10ms) respectively.
#   * The bandwidth and delay of the interface of lh2 have been changed from the
#     default values of (10mbit, 4ms) to (10mbit, 10ms) respectively.

################################################################################
#                              Network Topology                                #
#                                                                              #
#    <- 10mbit, 4ms ->                                    <- 10mbit, 4ms ->    #
# lh1 -------------------|                            |------------------- rh1 #
#           TCP          |                            |         TCP            #
#                        |                            |   <- 10mbit, 4ms ->    #
#                        |                            |------------------- rh2 #
#    <- 10mbit, 10ms ->  |      <- 20mbit, 10ms ->    |         TCP            #
# lh2 -------------------- r1 ---------------------- r2                        #
#           TCP          |                            |   <- 10mbit, 4ms ->    #
#                        |                            |------------------- rh3 #
#                        |                            |         TCP            #
#    <- 10mbit, 4ms ->   |                            |   <- 10mbit, 4ms ->    #
# lh3 -------------------|                            |------------------- rh4 #
#  1 TCP flow, 1 UDP flow                                       UDP            #
#                                                                              #
################################################################################

# Create a dumbbell topology with 3 left side nodes, 4 right side nodes and 2 routers,
# with IPv4 addresses (as the IPv6 flag is False) and FRR logging enabled (as the flag is True)
topology = DumbbellHelper({"left": 3, "right": 4, "routers": 2}, False, True)

# Configure the parameters of `fq_codel` qdisc
qdisc = "fq_codel"
fq_codel_parameters = {
    "limit": "100",  # set the queue capacity to 100 packets
    "target": "2ms",  # set the target queue delay to 2ms (default is 5ms)
    "interval": "24ms",  # set the interval value to 24ms (default is 100ms)
    "ecn": "",  # ECN is enabled
}

# Enable `fq-codel` queue discipline on the link from `r1` to `r2`, and update the
# bandwidth to 20mbit and delay to 10ms (defaults in DumbbellHelper are qdisc: pfifo,
# bandwidth: 10mbit and delay: 4ms)
topology.get_router_interface(0, -1).set_attributes(
    "20mbit", "10ms", qdisc, **fq_codel_parameters
)

# Changing the link attributes for the interface of lh2 (updating the bandwidth to 10mbit,
# delay to 10ms and qdisc to pfifo from the default values of 10mbit, 4ms and pfifo
# respectively). If the qdisc is not specified, kernel defaults would be used.
# All other interfaces use the default settings as defined in DumbbellHelper.
topology.get_left_interface(1).set_attributes("10mbit", "10ms", "pfifo")

# Set up an Experiment. This API takes the name of the experiment as a string.
exp = Experiment("dumbbell-custom-config-example")

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

# Enable collection of stats for `fq-codel` qdisc installed on
# `etr1d` interface, connecting `r1` to `r2`.
exp.require_qdisc_stats(topology.get_router_interface(0, -1))

# Run the experiment
exp.run()
