# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *

# This program emulates a point to point network between two hosts `h1` and
# `h2`. Five ping packets are sent from `h1` to `h2`, and the success/failure
# of these packets is reported.

#################################
#       Network Topology        #
#                               #
#          5mbit, 5ms -->       #
#   h1 ------------------- h2   #
#       <-- 10mbit, 100ms       #
#                               #
#################################

# Create two hosts, with the names h1 and h2
# and return it to the python variables `h1` and `h2`
# The `Node` API takes the name of the node as a string,
# and the same name is used to return results.
h1 = Node("h1")
h2 = Node("h2")

# Connect the above two hosts using a veth (virtual Ethernet)
# pair and return the interfaces at the end points of the link
# as a tuple `eth1` and `eth2`. `eth1` interface is at `h1` and
# `eth2` interface is at `h2`.
# The `connect` API takes two hosts as the parameters and returns
# the pair of interfaces.
(eth1, eth2) = connect(h1, h2)

# Assign IPv4 address to both the interfaces.
# The `set_address` API takes the address as a string.
# Note: it is important to mention the subnet.
eth1.set_address("192.168.1.1/24")
eth2.set_address("192.168.1.2/24")

# Set the link attributes such as bandwidth and propagation delay.
# The attributes for the link from `h1` to `h2` are set at
# interface `eth1` (and vice versa).
# Note that the bandwidth and propagation delay can be asymmetric.
# In the real deployments, upload and download bandwidth is not
# the same, and even propagation delays can vary because the
# forward and reverse paths can be different.
eth1.set_attributes("5mbit", "5ms")
eth2.set_attributes("10mbit", "100ms")

# `Ping` from `h1` to `h2`.
# The `ping` API, by default, sends five ping packets from `h1` to `h2`
# and reports whether they succeeded or failed.
h1.ping(eth2.address)
