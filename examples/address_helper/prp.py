# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT#
########################
from nest.experiment import *
from nest.topology import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper
from nest.routing.routing_helper import RoutingHelper

##############################
# Topology
#
# n1 -->-- r ---> n2
##############################

# Create Nodes
n2 = Node("n2")
r = Node("r")
n1 = Node("n1")

# Enable IP forwarding in routers
r.enable_ip_forwarding()

# Define networks
left_network = Network("::FFFF:10.0.0.0/124")
right_network = Network("::FFFF:11.0.0.0/124")

# Create interfaces and connect nodes and routers
(n1_r, r_n1) = connect(n1, r, network=left_network)
(r_n2, n2_r) = connect(r, n2, network=right_network)

# Assign addresses to each interface present in network
AddressHelper.assign_addresses()

# Routing
RoutingHelper(protocol="rip").populate_routing_tables()

# Sets attributes such as bandwidth, latency and
# queue discipline for the link.
n1_r.set_attributes("100mbit", "5ms")
r_n1.set_attributes("100mbit", "5ms")

r_n2.set_attributes("10mbit", "40ms", "pie")
n2_r.set_attributes("10mbit", "40ms")

# Adds two flows between the two nodes `n1` and `n2`
# The API takes in the source node, destination node,
# destination address, start time and end time of
# the flow and the number of flows
flow = Flow(n1, n2, n2_r.get_address(), 0, 20, 2)
flow_udp = Flow(n1, n2, n2_r.get_address(), 0, 20, 1)

exp = Experiment("tcp+udp")

# Add the above defined flows to the experiment.
# One of the flows added is udp and the other is
# tcp and an optional arguement of target bandwidth
# is given to the udp flow
exp.add_udp_flow(flow_udp, target_bandwidth="2mbit")
exp.add_tcp_flow(flow)
exp.require_qdisc_stats(r_n2)
exp.run()
