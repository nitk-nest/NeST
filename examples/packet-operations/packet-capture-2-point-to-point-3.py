# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper

# This program emulates point to point networks that connect two hosts `h1` and
# `h2` via two routers `r1` and `r2`. 10 ping packets are sent from `h1` to
# `h2`. It is similar to `ah-point-to-point-3.py` in `examples/address-helpers`.
# This program shows how to capture packets at `h2` by using `tcpdump`.
# The details of the packets captured at the `eth2` interface of `h2` are then
# written into `packet_capture.pcap` file.

##############################################################################
#                              Network Topology                              #
#                                                                            #
#        5mbit, 5ms -->         5mbit, 5ms -->           5mbit, 5ms -->      #
# h1 -------------------- r1 -------------------- r2 -------------------- h2 #
#     <-- 10mbit, 100ms       <-- 10mbit, 100ms       <-- 10mbit, 100ms      #
#                                                                            #
##############################################################################

# Create two hosts `h1` and `h2`, and two routers `r1` and `r2`
h1 = Node("h1")
h2 = Node("h2")
r1 = Router("r1")
r2 = Router("r2")

# Set the IPv4 address for the networks, and not the interfaces.
# We will use the `AddressHelper` later to assign addresses to the interfaces.
# Note: this example has three networks: one on the left of `r1`, second
# between the two routers, and third on the right of `r2`.
n1 = Network("192.168.1.0/24")  # network on the left of `r1`
n2 = Network("192.168.2.0/24")  # network between two routers
n3 = Network("192.168.3.0/24")  # network on the right of `r2`

# Connect `h1` to `r1`, `r1` to `r2`, and then `r2` to `h2`
# `eth1` and `eth2` are the interfaces at `h1` and `h2`, respectively.
# `etr1a` is the first interface at `r1` which connects it with `h1`
# `etr1b` is the second interface at `r1` which connects it with `r2`
# `etr2a` is the first interface at `r2` which connects it with `r1`
# `etr2b` is the second interface at `r2` which connects it with `h2`
(eth1, etr1a) = connect(h1, r1, network=n1)
(etr1b, etr2a) = connect(r1, r2, network=n2)
(etr2b, eth2) = connect(r2, h2, network=n3)

# Assign IPv4 addresses to all the interfaces in the network.
AddressHelper.assign_addresses()

# Set the link attributes: `h1` --> `r1` --> `r2` --> `h2`
eth1.set_attributes("5mbit", "5ms")  # from `h1` to `r1`
etr1b.set_attributes("5mbit", "5ms")  # from `r1` to `r2`
etr2b.set_attributes("5mbit", "5ms")  # from `r2` to `h2`

# Set the link attributes: `h2` --> `r2` --> `r1` --> `h1`
eth2.set_attributes("10mbit", "100ms")  # from `h2` to `r2`
etr2a.set_attributes("10mbit", "100ms")  # from `r2` to `r1`
etr1a.set_attributes("10mbit", "100ms")  # from `r1` to `h1`

# Set default routes in `h1` and `h2`. Additionally, set default routes in
# `r1` and `r2` so that the packets that cannot be forwarded based on the
# entries in their routing table are sent via a default interface.
h1.add_route("DEFAULT", eth1)
h2.add_route("DEFAULT", eth2)
r1.add_route("DEFAULT", etr1b)
r2.add_route("DEFAULT", etr2a)

# Capture a maximum of 30 packets on `eth2` interface of `h2`. Although we
# send just 10 ping packets, there are ping replies and other packets (such
# as ARP) to be captured. Hence, we capture a maximum of 30 packets.
# Output the details of the packets captured after 30 packets are captured,
# into `packet_capture.pcap` file.
h2.capture_packets(interface=eth2, packet_count=30, output_file="packet_capture.pcap")

# `Ping` from `h1` to `h2`. Send 10 ping packets.
h1.ping(eth2.address, packets=10)
