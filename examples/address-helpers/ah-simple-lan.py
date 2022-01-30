# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper

# This program emulates a Local Area Network (LAN). Four hosts: `h1` to `h4`
# are connected using a switch `s1`. Five ping packets are sent from `h1` to
# `h2`, and five ping packets from `h3` to `h4`. The success/failure of these
# packets are reported. It is similar to `simple-lan.py` available in
# `examples/basic-examples`, the only difference is that we use an address
# helper in this program to assign IPv4 addresses to interfaces instead of
# manually assigning them. Note that two packages: `Network` and
# `AddressHelper` are imported in this program (Lines 8-9 above).

######################################################################
#                          Network Topology                          #
#                                                                    #
#  h1               h2                          h3               h4  #
#  |                |                           |                 |  #
#  ----------------------------- s1 -------------------------------  #
#                    <------ 100mbit, 1ms ------>                    #
#                                                                    #
######################################################################

# Create four hosts `h1` to `h4`, and one switch `s1`
h1 = Node("h1")
h2 = Node("h2")
h3 = Node("h3")
h4 = Node("h4")
s1 = Switch("s1")

# Set the IPv4 address for the network, and not the interfaces.
# We will use the `AddressHelper` later to assign addresses to the interfaces.
n1 = Network("192.168.1.0/24")

# Connect all the four hosts to the switch
# `eth1` to `eth4` are the interfaces at `h1` to `h4`, respectively.
# `ets1a` is the first interface at `s1` which connects it with `h1`
# `ets1b` is the second interface at `s1` which connects it with `h2`
# `ets1c` is the third interface at `s1` which connects it with `h3`
# `ets1d` is the fourth interface at `s1` which connects it with `h4`
#
# Note: Since all the interfaces in this example belong to the same
# network, we demonstrate a simpler approach to use the `Network` API.
with n1:
    (eth1, ets1a) = connect(h1, s1)
    (eth2, ets1b) = connect(h2, s1)
    (eth3, ets1c) = connect(h3, s1)
    (eth4, ets1d) = connect(h4, s1)

# Assign IPv4 addresses to all the interfaces in the network.
AddressHelper.assign_addresses()

# Set the link attributes
eth1.set_attributes("100mbit", "1ms")
eth2.set_attributes("100mbit", "1ms")
eth3.set_attributes("100mbit", "1ms")
eth4.set_attributes("100mbit", "1ms")

# `Ping` from `h1` to `h2`, and `h3` to `h4`.
h1.ping(eth2.address)
h3.ping(eth4.address)
