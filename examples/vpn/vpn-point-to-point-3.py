# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2023 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper
from nest.topology.vpn import connect_vpn

# This program emulates point to point networks that connect two hosts `h1`
# and `h2` via two routers `r1` and `r2`. Five ping packets are sent from `h1`
# to `h2` once using Using the VPN endpoint address and once using Using the public address,
# and the success/failure of these packets is reported. It is similar to
# `ah-point-to-point-3.py` available in `examples/address-helpers`, the only
# difference is that we use `connect_vpn` API to create VPN tunnel between nodes.

##############################################################################
#                              Network Topology                              #
#                                                                            #
#        5mbit, 5ms -->          5mbit, 5ms -->          5mbit, 5ms -->      #
# h1 -------------------- r1 -------------------- r2 -------------------- h2 #
#     <-- 10mbit, 100ms       <-- 10mbit, 100ms       <-- 10mbit, 100ms      #
#                                                                            #
##############################################################################

# Create two hosts `h1` and `h2`, and two routers `r1` and `r2`
h1 = Node("h1")
h2 = Node("h2")
r1 = Router("r1")
r2 = Router("r2")

# Set the IPv4 address for the networks.
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

# Set up the VPN network with a private IPv4 address range.
# Make sure the chosen address range is not overlapping with any existing subnets on the network.
vpn_network = Network("10.200.0.0/24")

# For this address range the IP block 10.200.0.[0-3] is reserved for the OpenVPN server itself.
# The IP block 10.200.0.[4-7] is assigned to the first client, and subsequent clients are allocated
# consecutive IP addresses like 10.200.0.[8-11], [12-15], [16-19], and so on.

# Connect the VPN server and multiple clients using the `connect_vpn` API.
# By default, OpenVPN will work with Layer 3 and create a UDP tunnel using it's default port 1194.
# The `network` parameter specifies the network to allocate VPN endpoint addresses from.
# In this example, `vpn_network`, which is "10.200.0.0/24", is used for VPN endpoint addressing.

# Node `h1` acts as the VPN server and is assigned the IP address 10.200.0.1.
# When a client (e.g., `h2`) initiates a connection to the server on the designated port,
# it is allocated the VPN endpoint IP address 10.200.0.6 after the initial TLS handshake.

# Now, we establish the VPN connection between `h1` (VPN server) and `h2` (VPN client)
# using the `connect_vpn` API.
# The `connect_vpn` API returns the tunnel endpoints for `h1` (h1tun) and `h2` (h2tun).
(h1tun, h2tun) = connect_vpn(h1, h2, network=vpn_network)

# Once the VPN is established, we have created a secure alternate path between the nodes.
# This path is addressed using the tunnel endpoints which belongs to same private network.
# We have the flexibility to control which network traffic passes between the nodes over the VPN,
# and which traffic should go independently, not using the VPN.

# Using the VPN endpoint address to access `h2` from `h1`.
h1.ping(h2tun.address)

# Using the public address to access `h2` from `h1`.
# This traffic will not be sent through the VPN.
h1.ping(eth2.address)
