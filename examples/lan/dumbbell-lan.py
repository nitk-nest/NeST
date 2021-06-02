# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
import sys
from nest.experiment import *
from nest.topology import *

##############################
# Topology
#
#   n1----------------            ---------------- n4
#                     \         /
#   n2---------------- s1 ---- s2 ---------------- n5
#                     /         \
#   n3----------------            ---------------- n6
#
# "s1" and "s2" are switches.
##############################

###### TOPOLOGY CREATION ######

# Creating the switch for the LAN topology
s1 = Switch("s1")
s2 = Switch("s2")
n1 = Node("n1")
n2 = Node("n2")
n3 = Node("n3")
n4 = Node("n4")
n5 = Node("n5")
n6 = Node("n6")

print("Nodes and switch created")

# Add connections

(n1_s1, s1_n1) = connect(n1, s1)
(n2_s1, s1_n2) = connect(n2, s1)
(n3_s1, s1_n3) = connect(n3, s1)
(s1_s2, s2_s1) = connect(s1, s2)
(s2_n4, n4_s2) = connect(s2, n4)
(s2_n5, n5_s2) = connect(s2, n5)
(s2_n6, n6_s2) = connect(s2, n6)


print("Connections made")

###### ADDRESS ASSIGNMENT ######

n1_s1.set_address("10.0.0.1/24")
n2_s1.set_address("10.0.0.2/24")
n3_s1.set_address("10.0.0.3/24")
n4_s2.set_address("10.0.0.4/24")
n5_s2.set_address("10.0.0.5/24")
n6_s2.set_address("10.0.0.6/24")


print("Addresses are assigned")

####### ROUTING #######

# Setting up the attributes of the connections between
# the nodes and the switch
n1_s1.set_attributes("100mbit", "5ms")
n2_s1.set_attributes("100mbit", "5ms")
n3_s1.set_attributes("100mbit", "5ms")
n4_s2.set_attributes("100mbit", "5ms")
n5_s2.set_attributes("100mbit", "5ms")
n6_s2.set_attributes("100mbit", "5ms")
# Bottleneck link
s1_s2.set_attributes("10mbit", "40ms")
s2_s1.set_attributes("10mbit", "40ms")


######  RUN TESTS ######

# Giving the experiment a name
experiment = Experiment("dumbbell-lan")

# Add a flow from every node to another in the LAN

# from n1 to n4
flow = Flow(n1, n4, n4_s2.address, 0, 20, 1)
experiment.add_tcp_flow(flow)

# from n2 to n5
flow = Flow(n2, n5, n5_s2.address, 0, 20, 1)
experiment.add_tcp_flow(flow)

# from n3 to n6
flow = Flow(n3, n6, n6_s2.address, 0, 20, 1)
experiment.add_tcp_flow(flow)

# Running the experiment
experiment.run()
