# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper

# This program emulates two Local Area Networks (LANs) connected via a router.
# LAN-1 consists three hosts `h1` to `h3` connected to switch `s1`, and LAN-2
# consists three hosts `h4` to `h6` connected to switch `s2`. Switches `s1`
# and `s2` are connected to each other via a router `r1`. Five ping packets are
# sent from `h1` to `h4`, five from `h2` to `h5` and lastly, five from `h3` to
# `h6`. The success/failure of these packets is reported. It is similar to
# `two-lans-connected-via-router.py` available in `examples/basic-examples`,
# the only difference is that we use an address helper in this program to
# assign IPv4 addresses to interfaces instead of manually assigning them. Note
# that two packages: `Network` and `AddressHelper` are imported in this program
# (Lines 8-9 above).

##################################################################
#                       Network Topology                         #
#           LAN-1                           LAN-2                #
#   h1 ---------------                      --------------- h4   #
#                     \                    /                     #
#   h2 --------------- s1 ----- r1 ----- s2 --------------- h5   #
#                     /                    \                     #
#   h3 ---------------                      --------------- h6   #
#   <- 100mbit, 1ms ->  <- 10mbit, 10ms ->  <- 100mbit, 1ms ->   #
#                                                                #
##################################################################

# Create six hosts 'h1' to 'h6'
h1 = Node("h1")
h2 = Node("h2")
h3 = Node("h3")
h4 = Node("h4")
h5 = Node("h5")
h6 = Node("h6")

# Create two switches 's1' and 's2'
s1 = Switch("s1")
s2 = Switch("s2")

# Create a router 'r1'
r1 = Router("r1")

# Create two networks
n1 = Network("192.168.1.0/24")  # network on the left of `r1`
n2 = Network("192.168.2.0/24")  # network on the right of `r1`

# Create LAN-1: Connect hosts `h1`, `h2` and `h3` to switch `s1`
(eth1, ets1a) = connect(h1, s1, network=n1)
(eth2, ets1b) = connect(h2, s1, network=n1)
(eth3, ets1c) = connect(h3, s1, network=n1)

# Create LAN-2: Connect hosts `h4`, `h5` and `h6` to switch `s2`
(eth4, ets2a) = connect(h4, s2, network=n2)
(eth5, ets2b) = connect(h5, s2, network=n2)
(eth6, ets2c) = connect(h6, s2, network=n2)

# Connect switches `s1` and `s2` to router `r1`
(ets1d, etr1a) = connect(s1, r1, network=n1)
(ets2d, etr1b) = connect(s2, r1, network=n2)

# Assign IPv4 addresses to all the interfaces and switches in the network.
AddressHelper.assign_addresses()

# Set the attributes of the links between hosts and switches
eth1.set_attributes("100mbit", "1ms")
eth2.set_attributes("100mbit", "1ms")
eth3.set_attributes("100mbit", "1ms")
eth4.set_attributes("100mbit", "1ms")
eth5.set_attributes("100mbit", "1ms")
eth6.set_attributes("100mbit", "1ms")

# Set the attributes of the links between `r1` and switches
etr1a.set_attributes("10mbit", "10ms")
etr1b.set_attributes("10mbit", "10ms")

# Set the default routes for hosts `h1`, `h2` and `h3` via `etr1a`
h1.add_route("DEFAULT", eth1, etr1a.address)
h2.add_route("DEFAULT", eth2, etr1a.address)
h3.add_route("DEFAULT", eth3, etr1a.address)

# Set the default routes for hosts `h4`, `h5` and `h6` via `etr1b`
h4.add_route("DEFAULT", eth4, etr1b.address)
h5.add_route("DEFAULT", eth5, etr1b.address)
h6.add_route("DEFAULT", eth6, etr1b.address)

# `Ping` from `h1` to `h4`, `h2` to `h5`, and `h3` to `h6`.
h1.ping(eth4.address)
h2.ping(eth5.address)
h3.ping(eth6.address)
