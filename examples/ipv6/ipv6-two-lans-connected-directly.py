# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *

# This program emulates two Local Area Networks (LANs) connected directly to
# each other. LAN-1 consists three hosts `h1` to `h3` connected to switch `s1`,
# and LAN-2 consists three hosts `h4` to `h6` connected to switch `s2`.
# Switches `s1` and `s2` are connected to each other. Five ping packets are
# sent from `h1` to `h4`, five from `h2` to `h5`, and lastly, five `h3` to
# `h6`. The success/failure of these packets is reported. It is similar to
# `two-lans-connected-directly.py` available in `examples/basic-examples`, the
# only difference is that IPv6 addresses are used in this program.

#########################################################
#                    Network Topology                   #
#           LAN-1                      LAN-2            #
#   h1 ---------------            ---------------- h4   #
#                     \         /                       #
#   h2 --------------- s1 ---- s2 ---------------- h5   #
#                     /         \                       #
#   h3 ---------------            ---------------- h6   #
#             <------ 100mbit, 1ms ------>              #
#                                                       #
#########################################################

# Create six hosts `h1` to `h6`, and two switches `s1` and `s2`
h1 = Node("h1")
h2 = Node("h2")
h3 = Node("h3")
h4 = Node("h4")
h5 = Node("h5")
h6 = Node("h6")
s1 = Switch("s1")
s2 = Switch("s2")

# Create LAN-1: Connect hosts `h1`, `h2` and `h3` to switch `s1`
# `eth1` to `eth3` are the interfaces at `h1` to `h3`, respectively.
# `ets1a` is the first interface at `s1` which connects it with `h1`
# `ets1b` is the second interface at `s1` which connects it with `h2`
# `ets1c` is the third interface at `s1` which connects it with `h3`
(eth1, ets1a) = connect(h1, s1)
(eth2, ets1b) = connect(h2, s1)
(eth3, ets1c) = connect(h3, s1)

# Create LAN-2: Connect hosts `h4`, `h5` and `h6` to switch `s2`
# `eth4` to `eth6` are the interfaces at `h4` to `h6`, respectively.
# `ets2a` is the first interface at `s2` which connects it with `h4`
# `ets2b` is the second interface at `s2` which connects it with `h5`
# `ets2c` is the third interface at `s2` which connects it with `h6`
(eth4, ets2a) = connect(h4, s2)
(eth5, ets2b) = connect(h5, s2)
(eth6, ets2c) = connect(h6, s2)

# Connect switches `s1` and `s2`
# `ets1d` is the fourth interface at `s1` which connects it with `s2`
# `ets2d` is the fourth interface at `s2` which connects it with `s1`
(ets1d, ets2d) = connect(s1, s2)

# Assign IPv6 addresses to all the interfaces.
# We assume that the IPv6 address of this network is `2001::1/122`.
# Note: IP addresses should not be assigned to the interfaces on the switches.
eth1.set_address("2001::1:1/122")
eth2.set_address("2001::1:2/122")
eth3.set_address("2001::1:3/122")
eth4.set_address("2001::1:4/122")
eth5.set_address("2001::1:5/122")
eth6.set_address("2001::1:6/122")

# Set the link attributes
eth1.set_attributes("100mbit", "1ms")
eth2.set_attributes("100mbit", "1ms")
eth3.set_attributes("100mbit", "1ms")
eth4.set_attributes("100mbit", "1ms")
eth5.set_attributes("100mbit", "1ms")
eth6.set_attributes("100mbit", "1ms")

# `Ping` from `h1` to `h4`, `h2` to `h5`, and `h3` to `h6`.
h1.ping(eth4.address)
h2.ping(eth5.address)
h3.ping(eth6.address)
