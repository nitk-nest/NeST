# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *

# This program emulates a point to point network between two hosts `h1` and
# `h2`. Five ping packets are sent from `h1` to `h2`, and the success/failure
# of these packets is reported. It is similar to `point-to-point-1.py`
# available in `examples/basic-examples`, the only difference is that IPv6
# addresses are used in this program.

#################################
#       Network Topology        #
#                               #
#          5mbit, 5ms -->       #
#   h1 ------------------- h2   #
#       <-- 10mbit, 100ms       #
#                               #
#################################

# Create two hosts `h1` and `h2`
h1 = Node("h1")
h2 = Node("h2")

# Connect the above two hosts using a veth (virtual Ethernet) pair
(eth1, eth2) = connect(h1, h2)

# Assign IPv6 address to both the interfaces.
# We assume that the IPv6 address of this network is `2001::1/122`
eth1.set_address("2001::1:1/122")
eth2.set_address("2001::1:2/122")

# Set the link attributes: `h1` --> `h2` and `h2` --> `h1`
eth1.set_attributes("5mbit", "5ms")
eth2.set_attributes("10mbit", "100ms")

# `Ping` from `h1` to `h2`.
h1.ping(eth2.address)
