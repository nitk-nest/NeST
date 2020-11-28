# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.experiment import *
from nest.topology import *

##############################
# Topology
#
# n0 ----- n1
##############################

# Creates two nodes, with the names n0 and n1
# and returns it to the variables `n0` and `n1`
# The API takes in the name of the node as a string.
# This name is used while displaying results.
n0 = Node('n0')
n1 = Node('n1')

# Connects the above two nodes using a veth (virtual ethernet)
# pair and returns the interfaces at the end points of the link
# as a tuple `n0_n1` and `n1_n0`. `n0_n1` interface
# is at `n0` and `n1_n0` interface is at `n1`.
#
# The API takes two nodes as the parameters
# and returns the pair of interfaces
(n0_n1, n1_n0) = connect(n0, n1)

# Sets address to both the interfaces
# The API takes the address as a string
# The subnet also needs to be mentioned
n0_n1.set_address('10.0.0.1/24')
n1_n0.set_address('10.0.0.2/24')

# Sets attributes such as bandwidth, latency and
# queue discipline for the link.
# Attributes for the link from `n0` to `n1` are set at interface
# `n0_n1` (and vice versa)
# Note that the bandwidth (and latency) need not be the same in both
# diretions, as in the real life scenario where upload bandwidth is
# typically lower than download bandwidth
n0_n1.set_attributes('5mbit', '5ms', 'pfifo')
n1_n0.set_attributes('10mbit', '100ms', 'pfifo')

# Defines a flow between the two nodes `n0` and `n1`
# The API takes in the source node, destination node,
# destination address, start time and end time of
# the flow and the number of flows
flow = Flow(n0, n1, n1_n0.address, 0, 10, 2)

# Define an experiment to be run on the above topology.
# The API takes the experiment name as a string
exp = Experiment('tcp_2up')

# Add the above defined flow to the experiment.
# The TCP flavor of the traffic generated can be
# optionally given. Below we have chosen TCP Reno
exp.add_tcp_flow(flow, 'reno')

# The experiment is run on the above topology with
# the mentioned configurations.
exp.run()
