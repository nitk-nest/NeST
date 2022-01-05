# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
from nest.experiment import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper

# This program emulates a Local Area Network (LAN). Four hosts: `h1` to `h4`
# are connected using a switch `s1`. It is similar to the `ah-simple-lan.py`
# example in `examples/address-helpers`. Instead of `ping`, one UDP
# flow is configured from `h1` to `h2` and another from `h3` to `h4`.
# Address helper is used in this program to assign IPv4 addresses.

######################################################################
#                          Network Topology                          #
#                                                                    #
#  h1               h2                          h3               h4  #
#  |                |                           |                 |  #
#  ----------------------------- s1 -------------------------------  #
#                    <------ 100mbit, 1ms ------>                    #
#                                                                    #
######################################################################

# This program runs for 50 seconds and creates a new directory called
# `udp-simple-lan(date-timestamp)_dump`. It contains a `README` which
# provides details about the sub-directories and files within this directory.
# For this program, see the plots in `iperf3` and `ping` sub-directories.

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

# Set up an Experiment. This API takes the name of the experiment as a string.
exp = Experiment("udp-simple-lan")

# Configure one flow from `h1` to `h2` and another from `h3` to `h4`. We do not
# use it as a UDP flow yet.
flow1 = Flow(h1, h2, eth2.get_address(), 0, 50, 1)
flow2 = Flow(h3, h4, eth4.get_address(), 0, 50, 1)

# Use `flow1` and `flow2` as UDP flows, and set the rate at which these flows
# would send UDP packets.
exp.add_udp_flow(flow1, target_bandwidth="12mbit")
exp.add_udp_flow(flow2, target_bandwidth="12mbit")

# Run the experiment
exp.run()
