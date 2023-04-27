# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2022-2023 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
from nest.experiment import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper


# This program emulates point to point networks that connect two hosts `h1`
# and `h2` via two switches `s1` and `s2`. This program is similar to
# `udp-point-to-point-3.py` in `examples/udp`. One DCTCP flow
# is configured from `h1` to `h2`. The links between `h1` to `s1` and between
# `s2` to `h2` are edge links. The link between `s1` and `s2` is the bottleneck
# link with lesser bandwidth and higher propagation delays. `codel` queue
# discipline is enabled on the link from `s1` to `s2`, but not from `s2` to
# `s1` because data packets flow in one direction only (`h1` to `h2`) in this
# example.

##############################################################################
#                              Network Topology                              #
#                                                                            #
#      1000mbit, 1ms -->       10mbit, 10ms -->       1000mbit, 1ms -->      #
# h1 -------------------- s1 -------------------- s2 -------------------- h2 #
#     <-- 1000mbit, 1ms       <-- 10mbit, 10ms        <-- 1000mbit, 1ms      #
#                                                                            #
##############################################################################

# This program runs for 200 seconds and creates a new directory called
# `dctcp-point-to-point-3(date-timestamp)_dump`. It contains a `README` which
# provides details about the sub-directories and files within this directory.
# See the plots in `netperf`, `ping` and `ss` sub-directories for this program.

# Create two hosts `h1` and `h2`, and two switches `s1` and `s2`
s1 = Switch("s1")
s2 = Switch("s2")

h1 = Node("h1")
h2 = Node("h2")

# Set the IPv4 address for the network, and not the interfaces.
# We will use the `AddressHelper` later to assign addresses to the interfaces.
n1 = Network("192.168.1.0/24")

# Connect `h1` to `s1`, `s1` to `s2`, and then `s2` to `h2`
# `eth1` and `eth2` are the interfaces at `h1` and `h2`, respectively.
# `ets1a` is the first interface at `s1` which connects it with `h1`
# `ets1b` is the second interface at `s1` which connects it with `s2`
# `ets2a` is the first interface at `s2` which connects it with `s1`
# `ets2b` is the second interface at `s2` which connects it with `h2`
(eth1, ets1a) = connect(h1, s1, network=n1)
(ets1b, ets2a) = connect(s1, s2, network=n1)
(ets2b, eth2) = connect(s2, h2, network=n1)

# Assign IPv4 addresses to all the interfaces in the network.
AddressHelper.assign_addresses()

# Configure the parameters of `codel` qdisc to enable step marking with ECN,
# which is essential for DCTCP. For more details about `codel` in Linux,
# use this command on CLI: `man tc-codel`.
qdisc = "codel"
codel_parameters = {
    "limit": "1000",  # set the queue size to 1000 packets (default is 1000)
    "target": "10000ms",  # set the target queue delay to 10000ms (default is 5ms)
    "interval": "100ms",  # set the interval value to 100ms (default is 100ms)
    "ce_threshold": "40ms",  # ce_threshold = (17% of queue size in pckts * size of each packet * 8) / (bandwidth)
    "ecn": "",  # enables ecn marking for codel
}

# Set the link attributes: `h1` --> `s1` --> `s2` --> `h2`
# Note: we enable `codel` queue discipline on the link from `s1` to `s2`.
eth1.set_attributes("1000mbit", "1ms")  # from `h1` to `s1`
ets1b.set_attributes("10mbit", "10ms", qdisc, **codel_parameters)  # from `s1` to `s2`
ets2b.set_attributes("1000mbit", "1ms")  # from 's2' to 'h2

# Set the link attributes: `h2' --> `s2` --> `s1` --> `h1`
eth2.set_attributes("1000mbit", "1ms")  # from 'h2' to `s2`
ets2a.set_attributes("10mbit", "10ms")  # from `s2` to `s1`
ets1a.set_attributes("1000mbit", "1ms")  # from `s1` to `h1`

# Set up an Experiment. This API takes the name of the experiment as a string.
exp = Experiment("dctcp-point-to-point-3")

# Configure a flow from `h1` to `h2`. We do not use it as a TCP flow yet.
# The `Flow` API takes in the source node, destination node, destination IP
# address, start and stop time of the flow, and the total number of flows.
# In this program, start time is 0 seconds, stop time is 200 seconds and the
# number of flows is 1.
flow1 = Flow(h1, h2, eth2.get_address(), 0, 200, 1)

# Configure the TCP parameter to enable ECN by setting the parameter value to 2
# Note: DCTCP requires devices in a network to support ECN, hence we enable ECN
# on them.
h1.configure_tcp_param("ecn", "2")
s1.configure_tcp_param("ecn", "2")
s2.configure_tcp_param("ecn", "2")
h2.configure_tcp_param("ecn", "2")

# Use `flow1` as a DCTCP flow.
exp.add_tcp_flow(flow1, "dctcp")

# Enable collection of stats for `codel` qdisc installed on `ets1b` interface,
# connecting `s1` to `s2`.
exp.require_qdisc_stats(ets1b)

# Run the experiment
exp.run()
