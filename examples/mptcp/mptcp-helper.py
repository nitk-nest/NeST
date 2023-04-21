# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2023 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
from nest.experiment import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper

from nest import config

config.set_value("show_mptcp_checklist", True)

"""
# The topology for this example is borrowed from `mptcp-default-configuration.py`

# This program emulates a network that connects two hosts `h1` and `h2` via two
# routers R1, R2. Here, H2 is multihomed (has >=2 interfaces) and also
# multiaddressed (the 2 interfaces on H2 belong to different subnets). Hence,
# this topology can exhibit MPTCP behaviour if there are multiple paths between
# H1 and H2.

# The primary gain due to MPTCP is in throughput. This will be noticed due to
# aggregation of the two subflows between R2 and H2. Due to no other congestion
# zones in the network, if MPTCP works, we should see a throughput >10mbit.

# The primary purpose of this example is to show the usage of the MPTCP helper in
# NeST, and how it drastically reduces the setup effort for its users, while still
# delivering the required configuratrion and results.

################################################################################
#                                                                              #
#                               Network Topology                               #
#      ____                 ____                 ____                ____      #
#     |    |               |    |               |    |  5mbit,10ms  |    |     #
#     |    |  15mbit,10ms  |    |  10mbit,10ms  |    | ------------ |    |     #
#     | H1 | ------------- | R1 | ------------- | R2 |              | H2 |     #
#     |    |               |    |               |    | ------------ |    |     #
#     |____|               |____|               |____|  5mbit,10ms  |____|     #
#                                                                              #
################################################################################
"""

"""
Starting standard topology setup
"""

# In the topology, we can see 4 different subnets.
# * One between H1-R1
# * One between R1-R2
# * Two between R2-H2
network1 = Network("10.0.0.0/24")
network2 = Network("12.0.0.0/24")
network3 = Network("192.168.10.0/24")
network4 = Network("192.168.11.0/24")

# Create two MPTCP enabled hosts `h1` and `h2`, and the routers 'r1' and 'r2'.
h1 = Node("h1")
h2 = Node("h2")
r1 = Router("r1")
r2 = Router("r2")

# Connect `h1` to `h2` via `r1` and `r2` as per topology
(eth1a, etr1a) = connect(h1, r1, network=network1)
(etr1b, etr2a) = connect(r1, r2, network=network2)
(etr2b, eth2a) = connect(r2, h2, network=network3)
(etr2c, eth2b) = connect(r2, h2, network=network4)

# Assign IPv4 addresses to all the interfaces in the network.
AddressHelper.assign_addresses()

h1.add_route("DEFAULT", eth1a)
r1.add_route(eth2a.get_address(), etr1b)
r1.add_route(eth2b.get_address(), etr1b)
r2.add_route(eth1a.get_address(), etr2a)
h2.add_route(eth1a.get_address(), eth2a)
h2.add_route(eth1a.get_address(), eth2b)

# Shape all links as specified in the topology
eth1a.set_attributes("100mbit", "10ms")
etr1a.set_attributes("100mbit", "10ms")
etr1b.set_attributes("100mbit", "10ms")
etr2a.set_attributes("100mbit", "10ms")
etr2b.set_attributes("10mbit", "10ms")
etr2c.set_attributes("10mbit", "10ms")
eth2a.set_attributes("10mbit", "10ms")
eth2b.set_attributes("10mbit", "10ms")

"""
End of standard topology setup
"""

# Initialize a monitor to verify the MPTCP connection
# parameters after the experiment.
h2.add_mptcp_monitor()

# Run the experiment with the mptcp helper.
exp = Experiment("example-mptcp")

flow = Flow.setup_mptcp_connection(
    source_interface=eth1a,
    destination_interface=eth2a,
    start_time=0,
    stop_time=60,
    number_of_streams=1,
)

exp.add_mptcp_flow(flow)
exp.run()
