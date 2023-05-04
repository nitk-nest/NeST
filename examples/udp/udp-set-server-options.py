# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
from nest.experiment import Experiment, Flow
from nest.experiment.tools import Iperf3

# This program emulates configuration of iperf3 server on two Local Area
# Networks (LANs) connected directly to each other. LAN-1 consists three hosts
# `h1` to `h3` connected to switch `s1`, and LAN-2 consists three hosts `h4` to
# `h6` connected to switch `s2`. Switches `s1` and `s2` are connected to each
# other. Two UDP flows are created from `h1` to `h4` and one UDP flow is
# created from `h2` to `h4`. Host `h1` sends packets to `h4` for 10 sec. At `h4`
# output is reported at an interval of 1 sec. After 5 sec of the start of the
# program `h2` starts sending packets to `h4` for 10 sec which is reported at an
# interval of 0.5 sec.

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

# Assign IPv4 addresses to all the interfaces.
# We assume that the IPv4 address of this network is `192.168.1.0/24`.
# Note: IP addresses should not be assigned to the interfaces on the switches.
eth1.set_address("192.168.1.1/24")
eth2.set_address("192.168.1.2/24")
eth3.set_address("192.168.1.3/24")
eth4.set_address("192.168.1.4/24")
eth5.set_address("192.168.1.5/24")
eth6.set_address("192.168.1.6/24")

# Set the link attributes
eth1.set_attributes("100mbit", "1ms")
eth2.set_attributes("100mbit", "1ms")
eth3.set_attributes("100mbit", "1ms")
eth4.set_attributes("100mbit", "1ms")
eth5.set_attributes("100mbit", "1ms")
eth6.set_attributes("100mbit", "1ms")

# Assign  source, Destination, start time, end time and number of
# parallel flows to each udp flows
flow_udp_1 = Flow(h1, h4, eth4.get_address(), 0, 10, 2)
flow_udp_2 = Flow(h2, h4, eth4.get_address(), 5, 15, 1)

# iperf3_server_options API is used to configure iperf3 server options

exp = Experiment("udp_flow")
exp.add_udp_flow(
    flow_udp_1, server_options=Iperf3.server_option(s_interval=0.5, port_no=2345)
)
exp.add_udp_flow(
    flow_udp_2, client_options=Iperf3.client_option(interval=0.3, cport=1234)
)
exp.run()
