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
config.set_value("assign_random_names", False)

"""
# This program contains a bunch of hosts. Some of these (H1, H5)
# are not multihomed and multiaddressed and they cannot participate in MPTCP.
# Other hosts are MPTCP capable. As a test, 2 MPTCP flows are setup as follows.
# * H1 to H6
# * H2 to H6

# The experiment must show a notable bandwidth improvement on these flows (> 10 mbits).
# The key idea of this example is to illustrate what makes a flow MPTCP capable. This
# is shown by considering the 2 flows stated here, and reasoning out whether or not
# they will exhibit an MPTCP behaviour. The same is then verified through experimentation.

##################################################################################################################
#                                                                                                                #
#                                              Network Topology                                                  #
#                                                                                                                #
##################################################################################################################
#       ______                                                                                                   #
#      |      |                                                                                                  #
#      |  H1  | ______________________                                                                           #
#      |______|                       |                                                                          #
#                                     |                                                                          #
#       ______                        |                                        ______                            #
#      |      | ______________________|                                       |      |                           #
#      |  H2  | ____|____             |                               _______ |  R4  | _______                   #
#      |______|     |    |          ______                           |        |______|        |                  #
#                   |    |         |      |                          |                        |                  #
#       ______      |    |         |  R1  | ______       ______  ____|         ______         |____  ______      #
#      |      | ____|    |         |______|       |____ |      |              |      |              |      |     #
#      |  H3  | ____|____|          ______         ____ |  R3  | ------------ |  R5  | ------------ |  H6  |     #
#      |______|     |    |         |      | ______|     |______| ____         |______|         ____ |______|     #
#                   |    |         |  R2  |                          |                        |                  #
#       ______      |    |         |______|                          |         ______         |                  #
#      |      | ____|    |                                           |_______ |      | _______|                  #
#      |  H4  | _________|____________|                                       |  R6  |                           #
#      |______|                       |                                       |______|                           #
#                                     |                                                                          #
#       ______                        |                                                                          #
#      |      | ______________________|                                                                          #
#      |  H5  |                                                                                                  #
#      |______|                                                                                                  #
#                                                                                                                #
##################################################################################################################
#                                                                                                                #
#      Link shaping info:                                                                                        #
#                                                                                                                #
#      * H{1-5} - R{1-2} are all 1000 mbits / 1 ms links                                                         #
#      * R{1-6} - R{1-6} are all 10 mbits / 10 ms links                                                          #
#      * R{4-6} - H6     are all 1000 mbits / 1 ms links                                                          #
#                                                                                                                #
##################################################################################################################
"""

# Setup topology

subnets = [Network(f"10.0.{index}.0/24") for index in range(16)]

h1 = Node("h1")
h2 = Node("h2")
h3 = Node("h3")
h4 = Node("h4")
h5 = Node("h5")

r1 = Router("r1")
r2 = Router("r2")
r3 = Router("r3")
r4 = Router("r4")
r5 = Router("r5")
r6 = Router("r6")

h6 = Node("h6")
h6.add_mptcp_monitor()
h1.add_mptcp_monitor()
h2.add_mptcp_monitor()

(eth1a, etr1a) = connect(h1, r1, network=subnets[0])
(eth2a, etr1b) = connect(h2, r1, network=subnets[1])
(eth2b, etr2a) = connect(h2, r2, network=subnets[2])
(eth3a, etr1c) = connect(h3, r1, network=subnets[3])
(eth3b, etr2b) = connect(h3, r2, network=subnets[4])
(eth4a, etr1d) = connect(h4, r1, network=subnets[5])
(eth4b, etr2c) = connect(h4, r2, network=subnets[6])
(eth5a, etr2d) = connect(h5, r2, network=subnets[7])
(etr1e, etr3a) = connect(r1, r3, network=subnets[8])
(etr2e, etr3b) = connect(r2, r3, network=subnets[9])
(etr3c, etr4a) = connect(r3, r4, network=subnets[10])
(etr3d, etr5a) = connect(r3, r5, network=subnets[11])
(etr3e, etr6a) = connect(r3, r6, network=subnets[12])
(etr4b, eth6a) = connect(r4, h6, network=subnets[13])
(etr5b, eth6b) = connect(r5, h6, network=subnets[14])
(etr6b, eth6c) = connect(r6, h6, network=subnets[15])

AddressHelper.assign_addresses()

h1.add_route(eth6a.get_address(), eth1a)
h1.add_route(eth6b.get_address(), eth1a)
h1.add_route(eth6c.get_address(), eth1a)

h2.add_route(eth6a.get_address(), eth2a)
h2.add_route(eth6b.get_address(), eth2b)
h2.add_route(eth6c.get_address(), eth2b)

h3.add_route(eth6a.get_address(), eth3a)
h3.add_route(eth6b.get_address(), eth3b)
h3.add_route(eth6c.get_address(), eth3b)

h4.add_route(eth6a.get_address(), eth4a)
h4.add_route(eth6b.get_address(), eth4b)
h4.add_route(eth6c.get_address(), eth4b)

h5.add_route(eth6a.get_address(), eth5a)
h5.add_route(eth6b.get_address(), eth5a)
h5.add_route(eth6c.get_address(), eth5a)

r1.add_route(eth6a.get_address(), etr1e)
r1.add_route(eth6b.get_address(), etr1e)
r1.add_route(eth6c.get_address(), etr1e)

r2.add_route(eth6a.get_address(), etr2e)
r2.add_route(eth6b.get_address(), etr2e)
r2.add_route(eth6c.get_address(), etr2e)

r3.add_route(eth6a.get_address(), etr3c)
r3.add_route(eth6b.get_address(), etr3d)
r3.add_route(eth6c.get_address(), etr3e)

r3.add_route(eth1a.get_address(), etr3a)
r3.add_route(eth2a.get_address(), etr3a)
r3.add_route(eth3a.get_address(), etr3a)
r3.add_route(eth4a.get_address(), etr3a)
r3.add_route(eth2b.get_address(), etr3b)
r3.add_route(eth3b.get_address(), etr3b)
r3.add_route(eth4b.get_address(), etr3b)
r3.add_route(eth5a.get_address(), etr3b)

r4.add_route(eth1a.get_address(), etr4a)
r4.add_route(eth2a.get_address(), etr4a)
r4.add_route(eth2b.get_address(), etr4a)
r4.add_route(eth3a.get_address(), etr4a)
r4.add_route(eth3b.get_address(), etr4a)
r4.add_route(eth4a.get_address(), etr4a)
r4.add_route(eth4b.get_address(), etr4a)
r4.add_route(eth5a.get_address(), etr4a)

r5.add_route(eth1a.get_address(), etr5a)
r5.add_route(eth2a.get_address(), etr5a)
r5.add_route(eth2b.get_address(), etr5a)
r5.add_route(eth3a.get_address(), etr5a)
r5.add_route(eth3b.get_address(), etr5a)
r5.add_route(eth4a.get_address(), etr5a)
r5.add_route(eth4b.get_address(), etr5a)
r5.add_route(eth5a.get_address(), etr5a)

r6.add_route(eth1a.get_address(), etr6a)
r6.add_route(eth2a.get_address(), etr6a)
r6.add_route(eth2b.get_address(), etr6a)
r6.add_route(eth3a.get_address(), etr6a)
r6.add_route(eth3b.get_address(), etr6a)
r6.add_route(eth4a.get_address(), etr6a)
r6.add_route(eth4b.get_address(), etr6a)
r6.add_route(eth5a.get_address(), etr6a)

h6.add_route(eth1a.get_address(), eth6a)
h6.add_route(eth2a.get_address(), eth6a)
h6.add_route(eth2b.get_address(), eth6c)
h6.add_route(eth3a.get_address(), eth6a)
h6.add_route(eth3b.get_address(), eth6c)
h6.add_route(eth4a.get_address(), eth6a)
h6.add_route(eth4b.get_address(), eth6c)
h6.add_route(eth5a.get_address(), eth6c)

for interface in [
    eth1a,
    eth2a,
    eth2b,
    eth3a,
    eth3b,
    eth4a,
    eth4b,
    eth5a,
    etr1a,
    etr1b,
    etr1c,
    etr1d,
    etr2a,
    etr2b,
    etr2c,
    etr2d,
    etr4b,
    etr5b,
    etr6b,
    eth6a,
    eth6b,
    eth6c,
]:
    interface.set_attributes("1000mbit", "1ms")

for interface in [etr1e, etr2e, etr3a, etr3b, etr3c, etr3d, etr3e, etr4a, etr5a, etr6a]:
    interface.set_attributes("10mbit", "10ms")

"""
# This flow from H1 to H6 will not show MPTCP behaviour.
# The reason for this is that there is only one path from H6 to H1.

# One might argue that packets from H1 can take multiple routes to reach H6.
# However, there is only one return path and hence, a new subflow is not created.

# In order to have multiple paths visible from H6 to H1, a simple routing
# (using `ip route add ...`) does not suffice. One must write more controlled
# `ip rule add ...` commands to dispatch packets from H6 along different routes,
# based on the originating interface. Such capability is not provided by `ip route`
# suite and is currently not supported in NeST.

# This can be verified by looking at the output of the MPTCP monitor on H1.
# H6 signals H1 that 2 of its other interfaces are available for new MPTCP subflows.
# However, H1 is unable to create a new subflow to H6.
"""
flow1 = Flow(
    h1,
    h6,
    eth6a.get_address(),
    0,
    60,
    1,
    eth1a.get_address(),
)

"""
# This flow from H2 to H6 is a standard MPTCP example.
# It exhibits MPTCP behaviour.

# Note the difference between the 2 flows in this experiment.
# H1 has only 1 interface, whereas H2 has 2.
# Also, notice the routing from H6 to H2. There are 2 very distinct paths defined.

# This can be verified by looking at the output of the MPTCP monitor on H2.
# H6 signals H2 that 2 of its other interfaces are available for new MPTCP subflows.
# H2 is able to create a new subflow with this information.
"""
flow2 = Flow(
    h2,
    h6,
    eth6a.get_address(),
    0,
    60,
    1,
    eth2a.get_address(),
)

for host in [h1, h2, h3, h4, h5, h6]:
    host.set_mptcp_parameters(5, 5)

for interface in [eth1a, eth2a, eth2b, eth3a, eth3b, eth4a, eth4b, eth5a]:
    interface.enable_mptcp_endpoint(flags=["subflow"])

for interface in [eth6a, eth6b, eth6c]:
    interface.enable_mptcp_endpoint(flags=["signal"])

exp = Experiment("example-mptcp")
exp.add_mptcp_flow(flow1)
exp.add_mptcp_flow(flow2)
exp.run()
