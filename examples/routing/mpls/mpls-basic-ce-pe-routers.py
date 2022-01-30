# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper

# This program demonstrates how to set up a MPLS network that connects two
# customer edge (ce) routers `ce1` and `ce2` via two provider edge (pe) routers
# `pe1` and `pe2`. All routers are MPLS enabled. The labels are assigned
# manually and Penultimate Hop Popping (PHP) is used in this program. Address
# helper is used to assign the IPv4 addresses to the interfaces. Five ping
# packets are sent from `ce1` to `ce2`, and the success/failure of these
# packets is reported.

##################################################################################
#                                Network Topology                                #
#                                                                                #
#         Label: 101 -->           Label: 102 -->               PHP              #
#                                                                                #
#        50mbit, 5ms -->         10mbit, 10ms -->          50mbit, 5ms -->       #
# ce1 -------------------- pe1 -------------------- pe2 -------------------- ce2 #
#        <-- 50mbit, 5ms         <-- 10mbit, 10ms          <-- 50mbit, 5ms       #
#                                                                                #
#             PHP                <-- Label: 202            <-- Label: 201        #
#                                                                                #
##################################################################################

# Create two ce routers `ce1` and `ce2`, and two pe routers `pe1` and `pe2`
ce1 = Router("ce1")
ce2 = Router("ce2")
pe1 = Router("pe1")
pe2 = Router("pe2")

# Set the IPv4 address for the networks.
# This example has three networks: one on the left of `pe1`, second between
# the two `pe` routers, and third on the right of `pe2`.
n1 = Network("192.168.1.0/24")  # network on the left of `pe1`
n2 = Network("192.168.2.0/24")  # network between two `pe` routers
n3 = Network("192.168.3.0/24")  # network on the right of `pe2`

# Connect `ce1` to `pe1`, `pe1` to `pe2`, and then `pe2` to `ce2`
# `etce1` and `etce2` are the interfaces at `ce1` and `ce2`, respectively.
# `etpe1a` is the first interface at `pe1` which connects it with `ce1`
# `etpe1b` is the second interface at `pe1` which connects it with `pe2`
# `etpe2a` is the first interface at `pe2` which connects it with `pe1`
# `etpe2b` is the second interface at `pe2` which connects it with `ce2`
(etce1, etpe1a) = connect(ce1, pe1, network=n1)
(etpe1b, etpe2a) = connect(pe1, pe2, network=n2)
(etpe2b, etce2) = connect(pe2, ce2, network=n3)

# Assign IPv4 addresses to all the interfaces in the network.
AddressHelper.assign_addresses()

# Enable MPLS on all the interfaces in the network
etce1.enable_mpls()
etpe1a.enable_mpls()
etpe1b.enable_mpls()
etpe2a.enable_mpls()
etpe2b.enable_mpls()
etce2.enable_mpls()

# Configure MPLS routes: `ce1` --> `pe1` --> `pe2` --> `ce2`
ce1.add_route_mpls_push("192.168.3.0/24", etpe1a.address, 101)  # Push label 101
pe1.add_route_mpls_switch(101, etpe2a.address, 102)  # Replace label 101 by 102
pe2.add_route_mpls_pop(102, etce2.address)  # Pop label 102 (PHP)

# Configure MPLS routes: `ce2` --> `pe2` --> `pe1` --> `ce1`
ce2.add_route_mpls_push("192.168.1.0/24", etpe2b.address, 201)  # Push label 201
pe2.add_route_mpls_switch(201, etpe1b.address, 202)  # Replace label 201 by 202
pe1.add_route_mpls_pop(202, etce1.address)  # Pop label 202 (PHP)

# Set the link attributes: `ce1` --> `pe1` --> `pe2` --> `ce2`
etce1.set_attributes("50mbit", "5ms")  # from `ce1` to `pe1`
etpe1b.set_attributes("10mbit", "10ms")  # from `pe1` to `pe2`
etpe2b.set_attributes("50mbit", "5ms")  # from `pe2` to `ce2`

# Set the link attributes: `ce2` --> `pe2` --> `pe1` --> `ce1`
etce2.set_attributes("50mbit", "5ms")  # from `ce2` to `pe2`
etpe2a.set_attributes("10mbit", "10ms")  # from `pe2` to `pe1`
etpe1a.set_attributes("50mbit", "5ms")  # from `pe1` to `ce1`

# `Ping` from `ce1` to `ce2`.
ce1.ping(etce2.address)
