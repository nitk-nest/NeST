# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.experiment import *
from nest.topology import *
from nest.routing.routing_helper import RoutingHelper
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper

#############################################
# This is an implementation of multi-bottleneck topology
#
#                      n4      n6      n9
#                       \       \       \
#                        \       \       \
#                         \       \       \
#        n0-------r0------r1------r2------r3--------n8
#                 /       /\       \       \
#                /       /  \       \       \
#               /       /    \       \       \
#              n3      n1    n2      n5      n7
#############################################

r0_r1_bandwidth = "50mbit"
r1_r2_bandwidth = "150mbit"
r2_r3_bandwidth = "150mbit"

link_bandwidth = "150mbit"

r0_r1_latency = "0.25ms"
r1_r2_latency = "0.25ms"
r2_r3_latency = "0.25ms"

link_latency = "0.001ms"

qdisc = "codel"

r0_r1_qdisc_parameters = {
    "ce_threshold": "4.8ms",
    "limit": "1000",
    "target": "100ms",
    "ecn": "",
}
r1_r2_qdisc_parameters = {
    "ce_threshold": "1.6ms",
    "limit": "1000",
    "target": "100ms",
    "ecn": "",
}
r2_r3_qdisc_parameters = {
    "ce_threshold": "1.6ms",
    "limit": "1000",
    "target": "100ms",
    "ecn": "",
}

# Creating all the nodes
node = []
for i in range(10):
    node.append(Node("node" + str(i)))
    node[i].configure_tcp_param("ecn", "1")

# Creating all the routers
router = []
for i in range(4):
    router.append(Node("router" + str(i)))
    router[-1].enable_ip_forwarding()

# Define networks
network_A = Network("2001::/122")
network_B = Network("2002::/122")
network_C = Network("2003::/122")
network_D = Network("2004::/122")
network_E = Network("2005::/122")
network_F = Network("2006::/122")
network_G = Network("2007::/122")
network_H = Network("2008::/122")
network_I = Network("2009::/122")
network_J = Network("2010::/122")
network_K = Network("2011::/122")
network_L = Network("2012::/122")
network_M = Network("2013::/122")

# Create interfaces and connect nodes and routers
(r0_n0, n0_r0) = connect(router[0], node[0], network=network_A)
(r0_n3, n3_r0) = connect(router[0], node[3], network=network_B)
(r0_r1, r1_r0) = connect(router[0], router[1], network=network_C)
(r1_n1, n1_r1) = connect(router[1], node[1], network=network_D)
(r1_n2, n2_r1) = connect(router[1], node[2], network=network_E)
(r1_n4, n4_r1) = connect(router[1], node[4], network=network_F)
(r1_r2, r2_r1) = connect(router[1], router[2], network=network_G)
(r2_n5, n5_r2) = connect(router[2], node[5], network=network_H)
(r2_n6, n6_r2) = connect(router[2], node[6], network=network_I)
(r2_r3, r3_r2) = connect(router[2], router[3], network=network_J)
(r3_n7, n7_r3) = connect(router[3], node[7], network=network_K)
(r3_n8, n8_r3) = connect(router[3], node[8], network=network_L)
(r3_n9, n9_r3) = connect(router[3], node[9], network=network_M)

# Assign addresses to each interface present in network
AddressHelper.assign_addresses()

# Populate routing table using RIP.
# Internally uses quagga/frr. Refer `RoutingHelper` class
# on how to add custom quagga/frr configuration
RoutingHelper(protocol="rip").populate_routing_tables()

# Setting attributes to the interfaces on the nodes and the opposite end
for n in node:
    for i in n.interfaces:
        i.set_attributes(link_bandwidth, link_latency)
        i.pair.set_attributes(link_bandwidth, link_latency)

# Setting attributes for the interfaces between routers
r0_r1.set_attributes(r0_r1_bandwidth, r0_r1_latency, qdisc, **r0_r1_qdisc_parameters)
r1_r0.set_attributes(r0_r1_bandwidth, r0_r1_latency)

r1_r2.set_attributes(r1_r2_bandwidth, r1_r2_latency, qdisc, **r1_r2_qdisc_parameters)
r2_r1.set_attributes(r1_r2_bandwidth, r1_r2_latency)

r2_r3.set_attributes(r2_r3_bandwidth, r2_r3_latency, qdisc, **r2_r3_qdisc_parameters)
r3_r2.set_attributes(r2_r3_bandwidth, r2_r3_latency)

time = 120
# Adds  flows between the two nodes `n1` and `n2`
flows = []
flows.append(Flow(node[3], node[9], n9_r3.get_address(), 0, time, 1))
flows.append(Flow(node[1], node[8], n8_r3.get_address(), 0, time, 2))
flows.append(Flow(node[0], node[5], n5_r2.get_address(), 0, time, 3))

# Giving the experiment a name
gfc_exp = Experiment("gfc")

# Add the above defined flows to the experiment.
for flow in flows:
    gfc_exp.add_tcp_flow(flow)

# Request traffic control stats
gfc_exp.require_qdisc_stats(r0_r1)
gfc_exp.require_qdisc_stats(r1_r2)
gfc_exp.require_qdisc_stats(r2_r3)

# Running the experiment
gfc_exp.run()
