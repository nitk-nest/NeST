# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *

# This program emulates point to point networks that connect two hosts `h1`
# and `h2` via a router `r1`. Five ping packets are sent from `h1` to `h2`, and
# the success/failure of these packets is reported.

##########################################################
#                   Network Topology                     #
#                                                        #
#          5mbit, 5ms -->          5mbit, 5ms -->        #
#   h1 -------------------- r1 -------------------- h2   #
#       <-- 10mbit, 100ms        <-- 10mbit, 100ms       #
#                                                        #
##########################################################

# Create two hosts `h1` and `h2`, and one router `r1`
h1 = Node("h1")
h2 = Node("h2")
r1 = Router("r1")  # Internally, `Router` API enables IP forwarding in `r1`

# Connect `h1` to `r1`, and then `r1` to `h2`
# `eth1` and `eth2` are the interfaces at `h1` and `h2`, respectively.
# `etr1a` is the first interface at `r1` which connects it with `h1`
# `etr1b` is the second interface at `r1` which connects it with `h2`
(eth1, etr1a) = connect(h1, r1)
(etr1b, eth2) = connect(r1, h2)

# Assign IPv4 addresses to all the interfaces.
# Note: this example has two networks, one each on either side of `r1`.
# Assign IPv4 addresses to interfaces in the left side network. We assume
# that the IPv4 address of the left side network is `192.168.1.0/24`
eth1.set_address("192.168.1.1/24")
etr1a.set_address("192.168.1.2/24")

# Assign IPv4 addresses to interfaces in the right side network. We assume
# that the IPv4 address of the right side network is `192.168.2.0/24`
etr1b.set_address("192.168.2.1/24")
eth2.set_address("192.168.2.2/24")

# Set the link attributes: `h1` --> `r1` --> `h2`
eth1.set_attributes("5mbit", "5ms")  # from `h1` to `r1`
etr1b.set_attributes("5mbit", "5ms")  # from `r1` to `h2`

# Set the link attributes: `h2` --> `r1` --> `h1`
eth2.set_attributes("10mbit", "100ms")  # from `h2` to `r1`
etr1a.set_attributes("10mbit", "100ms")  # from `r1` to `h1`

# Set default routes in `h1` and `h2` so that the packets that cannot be
# forwarded based on the entries in their routing table are sent via a
# default interface.
h1.add_route("DEFAULT", eth1)
h2.add_route("DEFAULT", eth2)

# Get the routes from the routing table of a Node r1 of interface etr1a and etr1b
r1.print_routes_to_file(etr1a, etr1b)

# Get the all routes from the routing table of a Node r1
r1.print_routes_to_file()
