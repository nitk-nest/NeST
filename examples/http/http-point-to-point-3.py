# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.experiment import *
from nest.topology import *
from nest.experiment.experiment import HttpApplication

# This program emulates a Local Area Network (LAN). Four hosts: `h1` to `h4`
# are connected using a switch `s1`. Here, H4 is taken as the HTTP Server and
# H1, H2, H3 act as HTTP Clients. They generate load for the H$ server with
# varying number of connections and rate. The results of this HTTP experiment
# will be documented in the "examples/<Exp Name>(<Timestamp>)_dump" folder.

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

# Connect all the four hosts to the switch
# `eth1` to `eth4` are the interfaces at `h1` to `h4`, respectively.
# `ets1a` is the first interface at `s1` which connects it with `h1`
# `ets1b` is the second interface at `s1` which connects it with `h2`
# `ets1c` is the third interface at `s1` which connects it with `h3`
# `ets1d` is the fourth interface at `s1` which connects it with `h4`
(eth1, ets1a) = connect(h1, s1)
(eth2, ets1b) = connect(h2, s1)
(eth3, ets1c) = connect(h3, s1)
(eth4, ets1d) = connect(h4, s1)

# Assign IPv4 addresses to all the interfaces.
# We assume that the IPv4 address of this network is `192.168.1.0/24`.
# Note: IP addresses should not be assigned to the interfaces on the switch.
eth1.set_address("192.168.1.1/24")
eth2.set_address("192.168.1.2/24")
eth3.set_address("192.168.1.3/24")
eth4.set_address("192.168.1.4/24")

# Set the link attributes
eth1.set_attributes("100mbit", "1ms")
eth2.set_attributes("100mbit", "1ms")
eth3.set_attributes("100mbit", "1ms")
eth4.set_attributes("100mbit", "1ms")

# Create HTTP Experiment
exp = Experiment("HTTP Point to Point 3")

# Create first HTTP application with
# h1->h4
# port = 4004
# num_conns = 100
# rate = 15
# num-calls = 2
http_application1 = HttpApplication(
    h1, h4, eth4.get_address(), 4004, 100, 15, {"num-calls": 2}
)

# Create second HTTP application with
# h2->h4
# port = 4004
# num_conns = 200
# rate = 10
# num-calls = 2
http_application2 = HttpApplication(
    h2, h4, eth4.get_address(), 4004, 200, 10, {"num-calls": 2}
)

# Create third HTTP application with
# h3->h4
# port = 4004
# num_conns = 50
# rate = 5
# num-calls = 2
http_application3 = HttpApplication(
    h3, h4, eth4.get_address(), 4004, 50, 5, {"num-calls": 2}
)

# You can add the applications at once as a list as shown below
exp.add_http_application([http_application1, http_application2, http_application3])

# Run the experiment
exp.run()
