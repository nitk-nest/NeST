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
# and returns it to the python variables `n0` and `n1`
# The API takes in the name of the node as a string
# the same name is used to return results
n0 = Node('n0')
n1 = Node('n1')

# Connects the two namespaces using a veth pair
# and returns the interfaces as a touple to
# `n0_n1` and `n1_n0`
# The API takes two nodes as the parameters
# and the order does not matter
(n0_n1, n1_n0) = connect(n0, n1)

# Sets address to both the interfaces
# The API takes the address as a string
# The subnet also needs to be mentioned
n0_n1.set_address('10.0.0.1/24')
n1_n0.set_address('10.0.0.2/24')

# Sets attributes such as bandwidth, latency and
# queue descipline to the connectivity
# Note that the latency and bandwidth need not be the same,
# as in the real life scenario where upload bandwidth is
# lesser than download
n0_n1.set_attributes('5mbit', '5ms', 'pfifo')
n1_n0.set_attributes('10mbit', '100ms', 'pfifo')

# Sets up a flow between the two nodes
# The API takes in the source node, destination node,
# destination address, start time, end time of the
# experiment to be run and the number of flows
flow = Flow(n0, n1, n1_n0.address, 0, 10, 2)

# The name of the experiment of the is taken to
# return the results according with the name
# the flavour of tcp to be used is also given
exp = Experiment('tcp_1up')
exp.add_tcp_flow(flow, 'reno')

# The experiment is run with the topology and
# mentioned configurations
exp.run()
