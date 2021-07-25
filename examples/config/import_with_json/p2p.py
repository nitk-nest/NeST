# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.experiment import *
from nest.topology import *
from nest import config

# Imports config from the mentioned file and overwrites
# the default config values only for the ones provided
# in the new file
# If the file is named `nest-config.json` and placed in
# current directory, /etc or ~/ then, the config
# is automatically read without invoking the below function
config.import_custom_config("custom-config.json")


##############################
# Topology
#
# n1 ----- n2
#
##############################

# Creates two nodes, with the names n1 and n2
# and returns it to the python variables `n1` and `n2`
# The API takes in the name of the node as a string
# the same name is used to return results
n1 = Node("n1")
n2 = Node("n2")

# Connects the above two nodes using a veth (virtual Ethernet)
# pair and returns the interfaces at the end points of the link
# as a tuple `n1_n2` and `n2_n1`. `n1_n2` interface
# is at `n1` and `n2_n1` interface is at `n2`.
# The API takes two nodes as the parameters
# and returns the pair of interfaces
(n1_n2, n2_n1) = connect(n1, n2)

# Sets address to both the interfaces
# The API takes the address as a string
# The subnet also needs to be mentioned
n1_n2.set_address("10.0.0.1/24")
n2_n1.set_address("10.0.0.2/24")

# Sets attributes such as bandwidth, latency and
# queue discipline for the link.
# Attributes for the link from `n1` to `n2` are set at interface
# `n1_n2` (and vice versa)
# Note that the bandwidth (and latency) need not be the same in both
# directions, as in the real life scenario where upload bandwidth is
# typically lower than download bandwidth
n1_n2.set_attributes("5mbit", "5ms")
n2_n1.set_attributes("10mbit", "100ms")

# Defines a flow between the two nodes `n1` and `n2`
# The API takes in the source node, destination node,
# destination address, start time and end time of
# the flow and the number of streams
flow = Flow(n1, n2, n2_n1.address, 0, 120, 1)

# Define an experiment to be run on the above topology.
# The API takes the experiment name as a string
exp = Experiment("tcp_1up")

# Add the above defined flow to the experiment.
# The default TCP flavor used is 'cubic'
exp.add_tcp_flow(flow)

# The experiment is run on the above topology with
# the mentioned configurations.
exp.run()
