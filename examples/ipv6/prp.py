# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT#
########################
from nest.experiment import *
from nest.topology import *

##############################
# Topology
#
# n1 -->-- r1 -->-- n2
##############################

n2 = Node("n2")
r = Node("r")
n1 = Node("n1")
r.enable_ip_forwarding()

# Connects the above two nodes using a veth (virtual Ethernet)
# pair and returns the interfaces at the end points of the link
# as a tuple.
# The API takes two nodes as the parameters
# and returns the pair of interfaces
(n1_r, r_n1) = connect(n1, r)
(r_n2, n2_r) = connect(r, n2)

n1_r.set_address("10::1:1/122")
r_n1.set_address("10::1:2/122")
r_n2.set_address("10::2:2/122")
n2_r.set_address("10::2:1/122")

n1.add_route("DEFAULT", n1_r)
n2.add_route("DEFAULT", n2_r)

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
exp.add_udp_flow(flow_udp, target_bandwidth="100mbit")
exp.add_tcp_flow(flow)
exp.require_qdisc_stats(r_n2)
exp.run()
