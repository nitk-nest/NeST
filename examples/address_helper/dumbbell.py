# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
import sys
from nest.experiment import *
from nest.topology import *
from nest.routing.routing_helper import RoutingHelper
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper

##############################
# Topology: Dumbbell
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
##############################

# Checking if the right arguments are input
if len(sys.argv) != 3:
    print("usage: python3 dumbbell.py <number-of-left-nodes> <number-of-right-nodes>")
    sys.exit(1)

# Assigning number of nodes on either sides of the dumbbell according to input
num_of_left_nodes = int(sys.argv[1])
num_of_right_nodes = int(sys.argv[2])

###### TOPOLOGY CREATION ######

# Creating the routers for the dumbbell topology
left_router = Node("left-router")
right_router = Node("right-router")

# Enabling IP forwarding for the routers
left_router.enable_ip_forwarding()
right_router.enable_ip_forwarding()

# Lists to store all the left and right nodes
left_nodes = []
right_nodes = []

# Creating all the left and right nodes
for i in range(num_of_left_nodes):
    left_nodes.append(Node("left-node-" + str(i)))

for i in range(num_of_right_nodes):
    right_nodes.append(Node("right-node-" + str(i)))

# Define networks
left_network = Network("10.0.0.0/24")
right_network = Network("10.0.1.0/24")
middle_network = Network("10.0.2.0/24")

# Add connections

# Lists of tuples to store the interfaces connecting the router and nodes
left_node_connections = []
right_node_connections = []

# Connections of the left-nodes to the left-router
with left_network:
    for i in range(num_of_left_nodes):
        left_node_connections.append(connect(left_nodes[i], left_router))

# Connections of the right-nodes to the right-router
with right_network:
    for i in range(num_of_right_nodes):
        right_node_connections.append(connect(right_nodes[i], right_router))

# Connecting the two routers
(left_router_connection, right_router_connection) = connect(
    left_router, right_router, network=middle_network
)

###### ADDRESS ASSIGNMENT ######

# One way
AddressHelper.assign_addresses()

# Another way
# AddressHelper.assign_addresses(left_network)
# AddressHelper.assign_addresses(right_network)
# AddressHelper.assign_addresses(middle_network)

# Another another way
# AddressHelper.assign_addresses([left_network, right_network, middle_network])

####### ROUTING #######
# RoutingHelper(protocol="rip").populate_routing_tables()
for i in range(num_of_left_nodes):
    left_nodes[i].add_route("DEFAULT", left_node_connections[i][0])

# If the destination address for any packet in left-router is
# one of the left-nodes, forward the packet to that node
for i in range(num_of_left_nodes):
    left_router.add_route(
        left_node_connections[i][0].get_address(), left_node_connections[i][1]
    )

# If the destination address doesn't match any of the entries
# in the left-router's iptables forward the packet to right-router
left_router.add_route("DEFAULT", left_router_connection)

# If any packet needs to be sent from any right nodes, send it to right-router
for i in range(num_of_right_nodes):
    right_nodes[i].add_route("DEFAULT", right_node_connections[i][0])

# If the destination address for any packet in left-router is
# one of the left-nodes, forward the packet to that node
for i in range(num_of_right_nodes):
    right_router.add_route(
        right_node_connections[i][0].get_address(), right_node_connections[i][1]
    )

# If the destination address doesn't match any of the entries
# in the right-router's iptables forward the packet to left-router
right_router.add_route("DEFAULT", right_router_connection)

# Setting up the attributes of the connections between
# the nodes on the left-side and the left-router
for i in range(num_of_left_nodes):
    left_node_connections[i][0].set_attributes("100mbit", "5ms")
    left_node_connections[i][1].set_attributes("100mbit", "5ms")

# Setting up the attributes of the connections between
# the nodes on the right-side and the right-router
for i in range(num_of_right_nodes):
    right_node_connections[i][0].set_attributes("100mbit", "5ms")
    right_node_connections[i][1].set_attributes("100mbit", "5ms")


# Setting up the attributes of the connections between
# the two routers
left_router_connection.set_attributes("20mbit", "50ms", "pie")
right_router_connection.set_attributes("20mbit", "50ms", "pie")

######  RUN TESTS ######

# Giving the experiment a name
experiment = Experiment("tcp-on-dumbbell")

# Add a flow from the left nodes to respective right nodes
for i in range(min(num_of_left_nodes, num_of_right_nodes)):
    flow = Flow(
        left_nodes[i], right_nodes[i], right_node_connections[i][0].address, 0, 20, 1
    )
    # Use TCP reno
    experiment.add_tcp_flow(flow, "reno")

# Request traffic control stats
experiment.require_qdisc_stats(left_router_connection)
experiment.require_qdisc_stats(right_router_connection)

# Running the experiment
experiment.run()
