# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
from nest import config
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper
from nest.routing.routing_helper import RoutingHelper

# This program demonstrates how to set up a MPLS network that connects two
# customer edge (ce) routers `ce1` and `ce2` via two provider edge (pe) routers
# `pe1` and `pe2`, which are further connected via a provider (p) router. Only
# `pe` and `p` routers are MPLS enabled. `ce` routers do not use MPLS. The
# labels are assigned automatically using the Label Distribution Protocol (LDP).
# This program uses LDP from Free Range Routing (FRR) suite. Penultimate Hop
# Popping (PHP) is used in this program. Address helper is used to assign the
# IPv4 addresses to the interfaces. Five ping packets are sent from `ce1` to
# `ce2`, and the success/failure of these packets is reported.

###################################################################################
#                                Network Topology                                 #
#                                                                                 #
#                 Labels are auto-assigned using LDP ->                           #
#                               |                                                 #
#     50mbit, 5ms ->     10mbit, 10ms ->   10mbit, 10ms ->     50mbit, 5ms ->     #
# ce1 -------------- pe1 --------------- p --------------- pe2 -------------- ce2 #
#     <- 50mbit, 5ms     <- 10mbit, 10ms   <- 10mbit, 10ms     <- 50mbit, 5ms     #
#                                                |                                #
#                              <- Labels are auto-assigned using LDP              #
#                                                                                 #
###################################################################################

# Configure the program to use FRR suite (for LDP).
config.set_value("routing_suite", "frr")

# Create two `ce` routers, two `pe` routers and one `p` router
ce1 = Router("ce1")
ce2 = Router("ce2")
pe1 = Router("pe1")
pe2 = Router("pe2")
p = Router("p")

# Set the IPv4 address for the networks.
# This example has four networks: one on the left of `pe1`, second between
# `pe1` and `p`, third between `p` and `pe2`, and fourth on the right of `pe2`.
n1 = Network("192.168.1.0/24")  # network on the left of `pe1`
n2 = Network("192.168.2.0/24")  # network between `pe1` and `p`
n3 = Network("192.168.3.0/24")  # network between `p` and `pe2`
n4 = Network("192.168.4.0/24")  # network on the right of `pe2`

# Connect `ce1` to `pe1`, `pe1` to `p`, `p` to `pe2`, and `pe2` to `ce2`
# `etce1` and `etce2` are the interfaces at `ce1` and `ce2`, respectively.
# `etpe1a` is the first interface at `pe1` which connects it with `ce1`
# `etpe1b` is the second interface at `pe1` which connects it with `p`
# `etpa` is the first interface at `p` which connects it with `pe1`
# `etpb` is the second interface at `p` which connects it with `pe2`
# `etpe2a` is the first interface at `pe2` which connects it with `p`
# `etpe2b` is the second interface at `pe2` which connects it with `ce2`
(etce1, etpe1a) = connect(ce1, pe1, network=n1)
(etpe1b, etpa) = connect(pe1, p, network=n2)
(etpb, etpe2a) = connect(p, pe2, network=n3)
(etpe2b, etce2) = connect(pe2, ce2, network=n4)

# Assign IPv4 addresses to all the interfaces in the network.
AddressHelper.assign_addresses()

# Enable MPLS on the required interfaces in the network.
etpe1b.enable_mpls()
etpa.enable_mpls()
etpb.enable_mpls()
etpe2a.enable_mpls()

# Use LDP to auto-assign labels on MPLS enabled interfaces. LDP requires an IP
# based dynamic routing protocol to be already in place for it to find out the
# IP addresses. In this program, we use Open Shortest Path First (OSPF).
# Initially, the OSPF routing protocol runs as usual, and then LDP runs on
# the MPLS enabled routers: `pe` and `p`.
RoutingHelper("ospf", ldp_routers=[pe1, p, pe2]).populate_routing_tables()

# Add `sleep` time to allow LDP to install routes. Depending on the size of the
# topology, the amount of time specified for `sleep` may vary. The following
# two lines may be added as topology grows in size and complexity. Note: this
# example does not require `sleep` time as the topology is simple and small.
#
# from time import sleep
# sleep(20)

# Set the link attributes: `ce1` --> `pe1` --> `p` --> `pe2` --> `ce2`
etce1.set_attributes("50mbit", "5ms")  # from `ce1` to `pe1`
etpe1b.set_attributes("10mbit", "10ms")  # from `pe1` to `p`
etpb.set_attributes("10mbit", "10ms")  # from `p` to `pe2`
etpe2b.set_attributes("50mbit", "5ms")  # from `pe2` to `ce2`

# Set the link attributes: `ce2` --> `pe2` --> `p` --> `pe1` --> `ce1`
etce2.set_attributes("50mbit", "5ms")  # from `ce2` to `pe2`
etpe2a.set_attributes("10mbit", "10ms")  # from `pe2` to `p`
etpa.set_attributes("10mbit", "10ms")  # from `p` to `pe1`
etpe1a.set_attributes("50mbit", "5ms")  # from `pe1` to `ce1`

# `Ping` from `ce1` to `ce2`.
ce1.ping(etce2.address)
