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

n1_r.set_address("10.1.1.1/24")
r_n1.set_address("10.1.1.2/24")
r_n2.set_address("10.1.2.2/24")
n2_r.set_address("10.1.2.1/24")

n1.add_route("DEFAULT", n1_r)
n2.add_route("DEFAULT", n2_r)

# Sets attributes such as bandwidth, latency and
# queue discipline for the link.
n1_r.set_attributes("100mbit", "5ms")
r_n1.set_attributes("100mbit", "5ms")

r_n2.set_attributes("10mbit", "40ms", "pie")
n2_r.set_attributes("10mbit", "40ms")

# Sets packet corruption of 20% with 0.5% correlation rate
# between two packets getting corrupted
n1_r.set_packet_corruption("20%", "0.5%")

# Adds two flows between the two nodes `n1` and `n2`
# The API takes in the source node, destination node,
# destination address, start time and end time of
# the flow and the number of flows
flow = Flow(n1, n2, n2_r.get_address(), 0, 20, 2)

exp = Experiment("tcp")

# Add the above defined flows to the experiment.
# The flows added is tcp
exp.add_tcp_flow(flow)
exp.require_qdisc_stats(r_n2)
exp.run()
