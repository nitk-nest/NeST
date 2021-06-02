# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
import sys
from nest.experiment import *
from nest.topology import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper

##############################
# Topology
#
#   n1----------------
#                     \
#   n2---------------- \
#                     \ \
#   n3---------------- sw
#   .                 /
#   .                /
#   .               /
#   .              /
#   nk------------
#
# "sw" is a switch.
##############################

# Checking if the right arguments are input
if len(sys.argv) != 2:
    print("usage: python3 lan.py <number-of-nodes>")
    sys.exit(1)

# Checking if more than 1 number of nodes are input
if int(sys.argv[1]) < 2:
    print("number of nodes need to be greater than 1")
    sys.exit(1)

# Assigning number of nodes according to input
num_of_nodes = int(sys.argv[1])

###### TOPOLOGY CREATION ######

# Creating the switch for the LAN topology
sw = Switch("sw")

# List to store all the nodes
nodes = []

# Creating all the nodes
for i in range(num_of_nodes):
    nodes.append(Node("node-" + str(i)))

print("Nodes and switch created")

# Add connections

# List of tuples to store the interfaces connecting the switch and nodes
node_connections = []

# Connections of the nodes to the switch
with Network("10.0.0.0/24"):
    for i in range(num_of_nodes):
        node_connections.append(connect(nodes[i], sw))

print("Connections made")

###### ADDRESS ASSIGNMENT ######

AddressHelper.assign_addresses()

print("Addresses are assigned")

####### ROUTING #######

# Setting up the attributes of the connections between
# the nodes and the switch
for i in range(num_of_nodes):
    node_connections[i][0].set_attributes("100mbit", "5ms")
    node_connections[i][1].set_attributes("100mbit", "5ms")

######  RUN TESTS ######

# Giving the experiment a name
experiment = Experiment("simple-lan")

# Add a flow from every node to another in the LAN
for i in range(num_of_nodes):
    for j in range(num_of_nodes):
        if not i == j:
            flow = Flow(nodes[i], nodes[j], node_connections[j][0].address, 0, 20, 1)
            # Use TCP reno
            experiment.add_tcp_flow(flow, "reno")

# Running the experiment
experiment.run()
