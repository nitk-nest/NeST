# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2024 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
from nest.experiment import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper

# This program emulates point to point networks that connect two hosts `h1`
# and `h2` via two routers `r1` and `r2`.
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


# Define three networks/subnets for point-to-point links.
n1 = Network("192.168.1.0/24")  # network between h1 and r1
n2 = Network("192.168.2.0/24")  # network between r1 and r2
n3 = Network("192.168.3.0/24")  # network between r2 and h2

# Connect hosts and routers using the networks defined above
# Returns two interface for each link: one for each connected device
(eth1, etr1a) = connect(h1, r1, network=n1)  # h1 <-> r1
(etr1b, etr2a) = connect(r1, r2, network=n2)  # r1 <-> r2
(etr2b, eth2) = connect(r2, h2, network=n3)  # r2 <-> h2

# Automatically assign IP addresses to all interfaces in the networks
AddressHelper.assign_addresses()

# Set the link attributes: `h1` --> `r1` --> `r2` --> `h2`
eth1.set_attributes("10mbit", "5ms")  # from `h1` to `r1`
etr1b.set_attributes("10mbit", "5ms")  # from `r1` to `r2`
etr2b.set_attributes("10mbit", "5ms")  # from `r2` to `h2`

# Set the link attributes: `h2` --> `r2` --> `r1` --> `h1`
eth2.set_attributes("10mbit", "5ms")  # from `h2` to `r2`
etr2a.set_attributes("10mbit", "5ms")  # from `r2` to `r1`
etr1a.set_attributes("10mbit", "5ms")  # from `r1` to `h1`

# Set default routes in `h1` and `h2`. Additionally, set default routes in
# `r1` and `r2` so that the packets that cannot be forwarded based on the
# entries in their routing table are sent via a default interface.
h1.add_route("DEFAULT", eth1)
h2.add_route("DEFAULT", eth2)
r1.add_route("DEFAULT", etr1b)
r2.add_route("DEFAULT", etr2a)

# This example runs default branch scenario
exp = Experiment("sip-point-to-point-3")

# Set the experiment duration in seconds.
duration = 40

# Set target callrate for SIP Application,
# NeST uses target callrate as 10 if this argument is not passed.
callrate = 12

# There are three scenario options that can be passed as argument:
#   1) basic
#   2) branch
#   3) xml

# If scenario 3 is passed as scenario then next two arguments are for
# server_xml file and client xml file, if any of the argument is omitted.
# default scenario is used for it.

app = SipApplication(
    h1,  # client namespace
    h2,  # server namespace
    eth1.get_address(),  # client IP
    eth2.get_address(),  # server IP
    5050,  # server PORT
    duration,  # duration in seconds
    "basic",  # scenario
    callrate=callrate,  # callrate (calls per second)
)

exp.add_sip_application(app)
exp.run()
