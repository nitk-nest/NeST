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

"""
# This config option is useful when experimenting with NeST.
# When set to True, NeST will match the topology against a checklist.
# This checklist defines the necessary checks that must pass if an MPTCP
# behaviour is to be expected from the topology.

# Note that passing all checks is not a confirmation that MPTCP behaviour
# will be seen in the experiment for sure.
"""
config.set_value("show_mptcp_checklist", True)

"""
# This program emulates a network that connects two hosts `h1` and `h2` via two
# routers R1, R2. Here, H2 is multihomed (has >=2 interfaces) and also
# multiaddressed (the 2 interfaces on H2 belong to different subnets). Hence,
# this topology can exhibit MPTCP behaviour if there are multiple paths between
# H1 and H2.

# The primary gain due to MPTCP is in throughput. This will be noticed due to
# aggregation of the two subflows between R2 and H2. Due to no other congestion
# zones in the network, if MPTCP works, we should see a throughput >10mbit.

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

# Even though MPTCP is enabled by default, here is the API to do so manually.
h1.enable_mptcp()
h2.enable_mptcp()

"""
# add_mptcp_monitor() will run the MPTCP monitor on the specified node,
# during the experiment. The monitor shows the MPTCP connections and subflows
# created during the experiment with their flow information.

# The output is stored as a part of the experiment dump itself.
"""
h2.add_mptcp_monitor()

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

# Configure MPTCP parameters and flow for the topology.

## 1. Create a flow from eth1a to eth2a
flow = Flow(
    h1,
    h2,
    eth2a.get_address(),
    0,
    60,
    1,
    source_address=eth1a.get_address(),  # notice this new parameter
)

## 2. Allow H1 and H2 to allow 1 subflow creation each.
## 3. Enable eth1a on H1 as MPTCP subflow endpoint, to initiate suflow creation.
"""
`max_subflows` specifies the maximum number of destiadditional subflows allowed
for each MPTCP connection. Additional subflows can be created due to: incoming
accepted ADD_ADDR sub-option, local subflow endpoints, additional subflows
started by the peer.

`max_add_addr_accepted` specifies the maximum number of
incoming ADD_ADDR sub-options accepted for each MPTCP connection. After
receiving the specified number of ADD_ADDR sub-options, any other incoming one
will be ignored for the MPTCP connection lifetime.
"""
h1.set_mptcp_parameters(max_subflows=1, max_add_addr_accepted=1)
h2.set_mptcp_parameters(max_subflows=1, max_add_addr_accepted=1)
eth1a.enable_mptcp_endpoint(flags=["subflow"])
eth2b.enable_mptcp_endpoint(flags=["signal"])

# Run the experiment with the flow we just created.
exp = Experiment("example-mptcp")
exp.add_mptcp_flow(flow)
exp.run()
