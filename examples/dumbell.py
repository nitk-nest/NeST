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

left_router = Router('lr')
right_router = Router('rr')

left_nodes = []
right_nodes = []

for i in range(num_of_left_nodes):
    left_nodes.append(Node('ln'+str(i)))

for i in range(num_of_right_nodes):
    right_nodes.append(Node('rn'+str(i)))

print('Nodes and routers created')

# Add connections

left_node_connections = []
right_node_connections = []

for i in range(num_of_left_nodes):
    left_node_connections.append(connect(left_nodes[i], left_router))

for i in range(num_of_right_nodes):
    right_node_connections.append(connect(right_nodes[i], right_router))
    
(left_router_connection, right_router_connection) = connect(left_router, right_router)

print('Connections made')

###### ADDRESS ASSIGNMENT ######

# A subnet object to auto generate addresses in the same subnet
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

router_subnet = Subnet('10.0.2.0/24')
left_router_connection.set_address(router_subnet.get_next_addr())
right_router_connection.set_address(router_subnet.get_next_addr())

print('Addresses are assigned')

####### ROUTE #######

# Adding default routes
for i in range(num_of_left_nodes):
    left_nodes[i].add_route('DEFAULT', left_node_connections[i][1].get_address(), 
                                left_node_connections[i][0])

left_router.add_route('DEFAULT', right_router_connection.get_address(), 
                        left_router_connection)

for i in range(num_of_right_nodes):
    right_router.add_route(right_node_connections[i][0].get_address(), right_node_connections[i][0].get_address(), 
                                right_node_connections[i][1])

for i in range(num_of_right_nodes):
    right_nodes[i].add_route('DEFAULT', right_node_connections[i][1].get_address(), 
                                right_node_connections[i][0])

right_router.add_route('DEFAULT', left_router_connection.get_address(), 
                        right_router_connection)

for i in range(num_of_left_nodes):
    left_router.add_route(left_node_connections[i][0].get_address(), left_node_connections[i][0].get_address(), 
                                left_node_connections[i][1])

######  RUN TESTS ######

# (API not finalised from here on)
