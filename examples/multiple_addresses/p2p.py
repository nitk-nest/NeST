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
# The API takes the address as a string or a list of strings
# The subnet also needs to be mentioned
n1_n2.set_address(["10.1.1.1/24", "10::1:1/122"])
n2_n1.set_address(["10.1.1.2/24", "10::1:2/122"])

# Sets attributes such as bandwidth, latency and
# queue discipline for the link.
# Attributes for the link from `n1` to `n2` are set at interface
# `n1_n2` (and vice versa)
# Note that the bandwidth (and latency) need not be the same in both
# directions, as in the real life scenario where upload bandwidth is
# typically lower than download bandwidth
n1_n2.set_attributes("5mbit", "5ms", "pfifo")
n2_n1.set_attributes("10mbit", "100ms", "pfifo")

# Defines flows between the two nodes `n1` and `n2`
# The API takes in the source node, destination node,
# destination address, start time and end time of
# the flow and the number of flows
#
# `get_address` method used here will return:
#       * Tuple of 2 when both ipv4 and ipv6 addresses are required as (ipv4, ipv6)
#         else only the required type will be returned, error when both are False
#       * Each type will return an Address object when there is only one address and
#         as_list is False else returns list of Address objects
flow_ipv4_1 = Flow(n1, n2, n2_n1.get_address(ipv4=True, ipv6=False), 0, 10, 2)
flow_ipv6_1 = Flow(n1, n2, n2_n1.get_address(ipv4=False, ipv6=True), 0, 10, 2)

# Define an experiment to be run on the above topology.
# The API takes the experiment name as a string
exp_1 = Experiment("tcp_2up_1")

# Add the above defined flows to the experiment.
# The TCP flavor of the traffic generated can be
# optionally given. Below we have chosen TCP Reno
exp_1.add_tcp_flow(flow_ipv4_1, "reno")
exp_1.add_tcp_flow(flow_ipv6_1, "reno")

# The experiment is run on the above topology with
# the mentioned configurations.
exp_1.run()

# Adds more IP addresses to the interface
# The API takes the address as a string or a list of strings
# The subnet also needs to be mentioned
n1_n2.add_address(["10.1.1.3/24", "10::1:3/122"])
n2_n1.add_address(["10.1.1.4/24", "10::1:4/122"])

# Deletes earlier assigned IP addresses from the interface
# The API takes the address as a string or a list of strings
# The subnet also needs to be mentioned
n1_n2.del_address(["10.1.1.1/24", "10::1:1/122"])
n2_n1.del_address(["10.1.1.2/24", "10::1:2/122"])

# Defines flows between the two nodes `n1` and `n2`
# The API takes in the source node, destination node,
# destination address, start time and end time of
# the flow and the number of flows
flow_ipv4_2 = Flow(n1, n2, n2_n1.get_address(ipv4=True, ipv6=False), 0, 10, 2)
flow_ipv6_2 = Flow(n1, n2, n2_n1.get_address(ipv4=False, ipv6=True), 0, 10, 2)

# Define an experiment to be run on the above topology.
# The API takes the experiment name as a string
exp_2 = Experiment("tcp_2up_2")

# Add the above defined flows to the experiment.
# The TCP flavor of the traffic generated can be
# optionally given. Below we have chosen TCP Reno
exp_2.add_tcp_flow(flow_ipv4_2, "reno")
exp_2.add_tcp_flow(flow_ipv6_2, "reno")

# The experiment is run on the above topology with
# the mentioned configurations.
exp_2.run()
