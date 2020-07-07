# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
import sys

sys.path.append('../')
from nest.topology import *


##############################
# Topology: Dumbell
#
#   ln0----------------                      ---------------rn0
#                      \                    /
#   ln1---------------  \                  /  ---------------rn1
#                      \ \                / /
#   ln2---------------- lr ------------- rr ---------------- rn2
#   .                  /                    \                .
#   .                 /                      \               .
#   .                /                        \              .
#   .               /                          \             .
#   lnk------------                              ------------rnk
#
#
##############################

# Checking if the right arguements are input
if len(sys.argv) != 3:
    print('usage: python3 dumbell.py <number-of-left-nodes> <number-of-right-nodes>')
    sys.exit(1)

# Assigning number of nodes on either sides of the dumbel accordign to input
num_of_left_nodes = int(sys.argv[1])
num_of_right_nodes = int(sys.argv[2])

###### TOPOLOGY CREATION ######

# Creating the routers for the dumbel topology
left_router = Router('lr')
right_router = Router('rr')

# Lists to store all the left and right nodes
left_nodes = []
right_nodes = []

# Creating all the left and right nodes
for i in range(num_of_left_nodes):
    left_nodes.append(Node('ln'+str(i)))

for i in range(num_of_right_nodes):
    right_nodes.append(Node('rn'+str(i)))

print('Nodes and routers created')

# Add connections

# Lists of tuples to store the interfaces connecting th router and nodes
left_node_connections = []
right_node_connections = []

# Connections of the left side nodes to the left router
for i in range(num_of_left_nodes):
    left_node_connections.append(connect(left_nodes[i], left_router))

# Connections of the right side nodes to the right router
for i in range(num_of_right_nodes):
    right_node_connections.append(connect(right_nodes[i], right_router))

# Connecting the two routers
(left_router_connection, right_router_connection) = connect(
    left_router, right_router)

print('Connections made')

###### ADDRESS ASSIGNMENT ######

# A subnet object to auto generate addresses in the same subnet
# This subnet is used for all the left nodes and the left router
left_subnet = Subnet('10.0.0.0/24')

for i in range(num_of_left_nodes):
    # Copying a left node's interface and it's pair to temperory variables
    node_int = left_node_connections[i][0]
    router_int = left_node_connections[i][1]

    # Assigning addresses to the interfaces
    node_int.set_address(left_subnet.get_next_addr())
    router_int.set_address(left_subnet.get_next_addr())

# This subnet is used for all the right nodes and the right router
right_subnet = Subnet('10.0.1.0/24')

for i in range(num_of_right_nodes):
    # Copying a left node's interface and it's pair to temperory variables
    node_int = right_node_connections[i][0]
    router_int = right_node_connections[i][1]

    # Assigning addresses to the interfaces
    node_int.set_address(right_subnet.get_next_addr())
    router_int.set_address(right_subnet.get_next_addr())

# This subnet is used for the connections between the two routers
router_subnet = Subnet('10.0.2.0/24')

# Assigning addresses to the connections between the two routers
left_router_connection.set_address(router_subnet.get_next_addr())
right_router_connection.set_address(router_subnet.get_next_addr())

print('Addresses are assigned')

####### ROUTING #######

# If any packet needs to be sent from any left nodes, send it to left router
for i in range(num_of_left_nodes):
    left_nodes[i].add_route('DEFAULT', left_node_connections[i][0])

# If the destination address for any packet in left router is
# one of the left nodes, forward the packet to that node
for i in range(num_of_left_nodes):
    left_router.add_route(left_node_connections[i][0].get_address(), left_node_connections[i][1])

# If the destination address doesn't match any of the entries
# in the left router's iptables forward the packet to right router
left_router.add_route('DEFAULT', left_router_connection)

# If any packet needs to be sent from any right nodes, send it to right router
for i in range(num_of_right_nodes):
    right_nodes[i].add_route('DEFAULT', right_node_connections[i][0])

# If the destination address for any packet in left router is
# one of the left nodes, forward the packet to that node
for i in range(num_of_right_nodes):
    right_router.add_route(right_node_connections[i][0].get_address(), right_node_connections[i][1])

# If the destination address doesn't match any of the entries
# in the right router's iptables forward the packet to left router
right_router.add_route('DEFAULT', right_router_connection)


######  RUN TESTS ######

# (API not finalised from here on)
