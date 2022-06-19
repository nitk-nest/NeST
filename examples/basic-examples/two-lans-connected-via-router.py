# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *

# This program emulates two Local Area Networks (LANs) connected via a router.
# LAN-1 consists three hosts `h1` to `h3` connected to switch `s1`, and
# LAN-2 consists three hosts `h4` to `h6` connected to switch `s2`.Switches `s1`
# and `s2` are connected to each other via a router 'r1'. Five ping packets are
# sent from `h1` to `h4`, five from `h2` to `h5` and lastly, five from `h3`to `h6`.
# The success/failure of these packets is reported.

###############################################################
#                       Network Topology                      #
#           LAN-1                           LAN-2             #
#   h1 ---------------                  ---------------- h4   #
#                     \                /                      #
#   h2 --------------- s1 --- r1 --- s2 ---------------- h5   #
#                     /                \                      #
#   h3 ---------------                  ---------------- h6   #
#                                                             #
###############################################################

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

# Create LAN-1: Connect hosts `h1`, `h2` and `h3` to switch `s1`
(eth1, ets1a) = connect(h1, s1)
(eth2, ets1b) = connect(h2, s1)
(eth3, ets1c) = connect(h3, s1)

# Create LAN-2: Connect hosts `h4`, `h5` and `h6` to switch `s2`
(eth4, ets2a) = connect(h4, s2)
(eth5, ets2b) = connect(h5, s2)
(eth6, ets2c) = connect(h6, s2)

# Connect switches `s1` and `s2`
(ets1d, etr1) = connect(s1, r1)
(ets2d, etr2) = connect(s2, r1)

# Assign IPv4 addresses to all the interfaces of network on the left of router
# We assume that the IPv4 address of this network is `192.168.1.0/24`.
# Note: IP addresses should not be assigned to the interfaces on the switches.
eth1.set_address("192.168.1.1/24")
eth2.set_address("192.168.1.2/24")
eth3.set_address("192.168.1.3/24")
etr1.set_address("192.168.1.4/24")

# Assign address to the switch on the left of router
s1.set_address("192.168.1.5/24")

# Assign IPv4 addresses to all the interfaces of network on the right of router
# We assume that the IPv4 address of this network is `192.168.2.0/24`.
# Note: IP addresses should not be assigned to the interfaces on the switches.
eth4.set_address("192.168.2.1/24")
eth5.set_address("192.168.2.2/24")
eth6.set_address("192.168.2.3/24")
etr2.set_address("192.168.2.4/24")

# Assign address to the switch on the right of router
s2.set_address("192.168.2.5/24")

# Set the link attributes
eth1.set_attributes("100mbit", "1ms")
eth2.set_attributes("100mbit", "1ms")
eth3.set_attributes("100mbit", "1ms")
eth4.set_attributes("100mbit", "1ms")
eth5.set_attributes("100mbit", "1ms")
eth6.set_attributes("100mbit", "1ms")
etr1.set_attributes("1000mbit", "10ms")
etr2.set_attributes("1000mbit", "10ms")

# Set the default routes
h1.add_route("DEFAULT", eth1, etr1.address)
h2.add_route("DEFAULT", eth2, etr1.address)
h3.add_route("DEFAULT", eth3, etr1.address)
h4.add_route("DEFAULT", eth4, etr2.address)
h5.add_route("DEFAULT", eth5, etr2.address)
h6.add_route("DEFAULT", eth6, etr2.address)

# `Ping` from `h1` to `h4`, `h2` to `h5`, and `h3` to `h6`.
h1.ping(eth4.address)
h2.ping(eth5.address)
h3.ping(eth6.address)
