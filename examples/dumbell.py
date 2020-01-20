# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
import sys

sys.path.append('../')

from nest import *

##############################
# Topology: Dumbell
##############################

if len(sys.argv) != 3:
    print('usage: python3 dumbell.py <number-of-left-nodes> <number-of-right-nodes>')
    sys.exit(1)

num_of_left_nodes = int(sys.argv[1])
num_of_right_nodes = int(sys.argv[2])

###### TOPOLOGY CREATION ######

left_router = Router('left-router')
right_router = Router('right_router')

left_nodes = []
right_nodes = []

for i in range(num_of_left_nodes):
    left_nodes.append(Node('left-node-'+i))

for i in range(num_of_right_nodes):
    right_nodes.append(Node('right-node'+i))

print('Nodes and routers created')

# Add connections

left_node_connections = []
right_node_connections = []

for i in range(num_of_left_nodes):
    left_node_connections.append(connect(left_nodes[i], left_router))

for i in range(num_of_right_nodes):
    right_node_connections.append(connect(right_nodes[i], right_router))
    
print('Connections made')

###### ADDRESS ASSIGNMENT ######

left_subnet = Subnet('10.0.0.0/24')

for i in range(num_of_left_nodes):
    node_int = left_node_connections[i][0]
    router_int = left_node_connections[i][1]

    node_int.set_address(left_subnet.get_next_addr())
    router_int.set_address(left_subnet.get_next_addr())

right_subnet = Subnet('10.0.1.0/24')

for i in range(num_of_right_nodes):
    node_int = right_node_connections[i][0]
    router_int = right_node_connections[i][1]

    node_int.set_address(right_subnet.get_next_addr())
    router_int.set_address(right_subnet.get_next_addr())

print('Addresses are assigned')

####### ROUTE #######

# Add routes
