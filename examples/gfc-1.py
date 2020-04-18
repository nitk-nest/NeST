# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
import sys

sys.path.append('../')

from nest.topology import *
from nest.test import *

#############################################
# This is an implementation of gfc-1 topology
# GFC Topology:
#                      n9     n11      n6    n8      n10
#                       \       \       \    /       /
#                        \       \       \  /       /
#                         \       \       \/       /
#         n0------r0------r1------r2------r3------r4------n7
#                 /       /\       \       \
#                /       /  \       \       \
#               /       /    \       \       \
#              n3      n1    n5      n2      n4
#############################################

r0_r1_bandwidth = input('Enter the bandwidth between r0 and r1\n')
r1_r2_bandwidth = input('Enter the bandwidth between r1 and r2\n')
r2_r3_bandwidth = input('Enter the bandwidth between r2 and r3\n')
r3_r4_bandwidth = input('Enter the bandwidth between r3 and r4\n')

link_bandwidth = input('Enter the bandwidth between the routers and the nodes\n')

r0_r1_latency = input('Enter the latency between r0 and r1\n')
r1_r2_latency = input('Enter the latency between r1 and r2\n')
r2_r3_latency = input('Enter the latency between r2 and r3\n')
r3_r4_latency = input('Enter the latency between r3 and r4\n')

link_latency = input('Enter the latency between the routers and the nodes\n')

qdisc = input('Enter the Queueing algorithm to be installed on the routers\n')

# Creating all the nodes
node = []
for i in range (12):
    node.append(Node('node' + str(i)))

# Creating all the routers
router = []
for i in range (5):
    router.append(Router('router' + str(i)))

# Making the necessary connections
(r0_n0, n0_r0) = connect(router[0], node[0])
(r1_n1, n1_r1) = connect(router[1], node[1])
(r0_n3, n3_r0) = connect(router[0], node[3])
(r1_n5, n5_r1) = connect(router[1], node[5])
(r2_n2, n2_r2) = connect(router[2], node[2])
(r3_n4, n4_r3) = connect(router[3], node[4])
(r1_r0, r0_r1) = connect(router[1], node[0])
(r2_r1, r1_r2) = connect(router[2], node[1])
(r3_r2, r2_r3) = connect(router[3], node[2])
(r4_r3, r3_r4) = connect(router[4], node[3])
(r3_n6, n6_r3) = connect(router[3], node[6])
(r4_n7, n7_r4) = connect(router[4], node[7])
(r1_n9, n9_r1) = connect(router[1], node[9])
(r2_n11, n11_r2) = connect(router[2], node[11])
(r3_n8, n8_r3) = connect(router[3], node[8])
(r4_n10, n10_r4) = connect(router[4], node[10])

# Setting addresses to the interfaces
n0_r0.set_address('10.0.1.1/24')
n6_r3.set_address('10.0.6.6/24')
n1_r1.set_address('10.0.11.1/24')
n7_r4.set_address('10.0.18.5/24')
n3_r0.set_address('10.0.9.1/24')
n9_r1.set_address('10.0.10.1/24')
n5_r1.set_address('10.0.12.1/24')
n11_r2.set_address('10.0.13.1/24')
n2_r2.set_address('10.0.14.1/24')
n8_r3.set_address('10.0.15.2/24')
n4_r3.set_address('10.0.16.3/24')
n10_r4.set_address('10.0.17.5/24')
r1_n9.set_address('10.0.10.3/24')
r0_n0.set_address('10.0.1.2/24')
r0_n3.set_address('10.0.9.2/24')
r0_r1.set_address('10.0.2.2/24')
r1_n1.set_address('10.0.11.3/24')
r1_r0.set_address('10.0.2.3/24')
r1_r2.set_address('10.0.3.3/24')
r1_n5.set_address('10.0.12.3/24')
r2_r1.set_address('10.0.3.4/24')
r2_r3.set_address('10.0.4.4/24')
r2_n11.set_address('10.0.13.4/24')
r2_n2.set_address('10.0.14.4/24')
r3_n6.set_address('10.0.6.5/24')
r3_n8.set_address('10.0.15.5/24')
r3_r2.set_address('10.0.4.5/24')
r3_r4.set_address('10.0.5.5/24')
r3_n4.set_address('10.0.16.5/24')
r4_r3.set_address('10.0.5.6/24')
r4_n7.set_address('10.0.18.6/24')
r4_n10.set_address('10.0.17.6/24')

# Adding default routes and subnet specific routes to route the network
node[0].add_route('DEFAULT', n0_r0)
node[6].add_route('DEFAULT', n6_r3)
router[4].add_route('DEFAULT', r4_r3)

router[0].add_route('DEFAULT', r0_r1)
router[1].add_route('DEFAULT', r1_r2)
router[3].add_route('DEFAULT', r3_r4)

node[1].add_route('DEFAULT', n1_r1)
node[7].add_route('DEFAULT', n7_r4)
router[3].add_route(r4_n7.get_subnet(), r3_r4)
router[2].add_route(r1_n1.get_subnet(), r2_r1)
router[2].add_route(r4_n7.get_subnet(), r2_r3)
router[3].add_route(r1_n1.get_subnet(), r3_r2)

node[3].add_route('DEFAULT', n3_r0)
node[9].add_route('DEFAULT', n9_r1)
router[1].add_route(r0_n3.get_subnet(), r1_r0)
router[0].add_route(r1_n9.get_subnet(), r0_r1)

node[5].add_route('DEFAULT', n5_r1)
node[11].add_route('DEFAULT', n11_r2)
router[1].add_route(r2_n11.get_subnet(), r1_r2)
router[2].add_route(r1_n5.get_subnet(), r2_r1)

node[2].add_route('DEFAULT', n2_r2)
node[8].add_route('DEFAULT', n8_r3)
router[2].add_route(r3_n8.get_subnet(), r2_r3)
router[3].add_route(r2_n2.get_subnet(), r3_r2)

node[4].add_route('DEFAULT', n4_r3)
node[10].add_route('DEFAULT', n10_r4)
router[3].add_route(r4_n10.get_subnet(), r3_r4)
router[4].add_route(r3_n4.get_subnet(), r4_r3)

router[1].add_route(r3_n6.get_subnet(), r1_r2)
router[2].add_route(r3_r4.get_subnet(), r2_r3)
router[2].add_route(r3_n6.get_subnet(), r2_r3)
router[3].add_route(r0_n0.get_subnet(), r3_r2)
router[2].add_route(r0_n0.get_subnet(), r2_r1)
router[1].add_route(r0_r1.get_subnet(), r2_r1)
router[1].add_route(r0_n0.get_subnet(), r1_r0)

# Setting attributes to the interfaces on the nodes and the opposite end
for n in node:
    for i in n.interface_list:
        i.set_attributes(link_bandwidth, link_latency)
        i.get_pair().set_attributes(link_bandwidth, link_latency)

# Setting attributes for the interfaces between routers
r0_r1.set_attributes(r0_r1_bandwidth, r0_r1_latency, qdisc)
r1_r0.set_attributes(r0_r1_bandwidth, r0_r1_latency, qdisc)

r1_r2.set_attributes(r1_r2_bandwidth, r1_r2_latency, qdisc)
r2_r1.set_attributes(r1_r2_bandwidth, r1_r2_latency, qdisc)

r2_r3.set_attributes(r2_r3_bandwidth, r2_r3_latency, qdisc)
r3_r2.set_attributes(r2_r3_bandwidth, r2_r3_latency, qdisc)

r3_r4.set_attributes(r3_r4_bandwidth, r3_r4_latency, qdisc)
r4_r3.set_attributes(r3_r4_bandwidth, r3_r4_latency, qdisc)