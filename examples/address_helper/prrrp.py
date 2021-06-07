# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT#
########################
from nest.experiment import *
from nest.topology import *
from nest.routing.routing_helper import RoutingHelper
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper

##############################
# Topology
#
# n1 -->-- r1 -->-- r2 -->-- r3 -->-- n2
#
##############################

### Create Nodes ###
n1 = Node("n1")
n2 = Node("n2")
r1 = Node("r1")
r2 = Node("r2")
r3 = Node("r3")

### Enable IP forwarding in routers ###
r1.enable_ip_forwarding()
r2.enable_ip_forwarding()
r3.enable_ip_forwarding()

# Define networks
net1 = Network("10.0.1.0/24")
net2 = Network("10.0.2.0/24")
net3 = Network("10.0.3.0/24")
net4 = Network("10.0.4.0/24")

# The API takes two nodes and network as the parameters
# where network is optional parameters
# It returns the pair of interfaces
# And it also add the interfaces to the network if mentioned
(n1_r1, r1_n1) = connect(n1, r1, network=net1)
(r1_r2, r2_r1) = connect(r1, r2, network=net2)
(r2_r3, r3_r2) = connect(r2, r3, network=net3)
(r3_n2, n2_r3) = connect(r3, n2, network=net4)

# Assign addresses to each interface present in network
AddressHelper.assign_addresses()

# Routing
RoutingHelper(protocol="rip").populate_routing_tables()

# Sets attributes such as bandwidth, latency and queue discipline for the link
n1_r1.set_attributes("100mbit", "5ms")
r1_n1.set_attributes("100mbit", "5ms")

r1_r2.set_attributes("10mbit", "40ms", "pie")
r2_r1.set_attributes("10mbit", "40ms", "pie")

r2_r3.set_attributes("10mbit", "40ms", "pie")
r3_r2.set_attributes("10mbit", "40ms", "pie")

r3_n2.set_attributes("100mbit", "5ms", "pie")
n2_r3.set_attributes("100mbit", "5ms")

# Adds two flows between the two nodes `n1` and `n2`
# The API takes in the source node, destination node,
# destination address, start time and end time of
# the flow and the number of flows
flow = Flow(n1, n2, n2_r3.get_address(), 0, 20, 2)
flow_udp = Flow(n1, n2, n2_r3.get_address(), 0, 20, 1)

# Giving the experiment a name
exp = Experiment("tcp+udp")

# Add the above defined flows to the experiment.
# One of the flows added is udp and the other is
# tcp and an optional arguement of target bandwidth
# is given to the udp flow
exp.add_udp_flow(flow_udp, target_bandwidth="2mbit")
exp.add_tcp_flow(flow)

# Request traffic control stats
exp.require_qdisc_stats(r1_r2)
exp.require_qdisc_stats(r2_r3)
exp.require_qdisc_stats(r3_n2)

# Running the experiment
exp.run()
