# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.experiment import *
from nest.topology import *

################################################
# Topology
#
#   peer-1 --- router-1 --- router-2 --- peer-2
#       --(101)->    --(102)->
#                    <-(202)--    <-(201)--
# We use penultimate hop popping here
# Labels are specified in brackets                       
################################################

### Set log level ###

# logging.set_log_level(2)

### Create Nodes ###

peer1 = Node('peer-1')
peer2 = Node('peer-2')
router1 = Node('router-1')
router2 = Node('router-2')

### Enable ip forwarding in routers ###

router1.enable_ip_forwarding()
router2.enable_ip_forwarding()


### Create interfaces and connect nodes and routers ###

(eth_p1r1, eth_r1p1) = connect(peer1, router1, 'eth-p1r1-0', 'eth-r1p1-0')
(eth_r1r2, eth_r2r1) = connect(router1, router2, 'eth-r1r2-0', 'eth-r2r1-0')
(eth_r2p2, eth_p2r2) = connect(router2, peer2, 'eth-r2p2-0', 'eth-p2r2-0')

### Assign addresses to interfaces ###

eth_p1r1.set_address('10.0.1.1/24')
eth_r1p1.set_address('10.0.1.2/24')

eth_r1r2.set_address('10.0.2.2/24')
eth_r2r1.set_address('10.0.2.3/24')

eth_r2p2.set_address('10.0.3.3/24')
eth_p2r2.set_address('10.0.3.4/24')


## Enable MPLS on the interfaces and implicitly on the nodes too
eth_p1r1.enable_mpls()
eth_r1p1.enable_mpls()

eth_r1r2.enable_mpls()
eth_r2r1.enable_mpls()

eth_r2p2.enable_mpls()
eth_p2r2.enable_mpls()

### Routing ###
print(eth_p2r2.address)
peer1.add_route_mpls_push('10.0.3.0/24', eth_r1p1.address, 101)
router1.add_route_mpls_switch(101, eth_r2r1.address, 102)
router2.add_route_mpls_pop(102, eth_p2r2.address)


peer2.add_route_mpls_push('10.0.1.0/24', eth_r2p2.address, 201)
router2.add_route_mpls_switch(201, eth_r1r2.address, 202)
router1.add_route_mpls_pop(202, eth_p1r1.address)

peer1.ping(eth_p2r2.address, True)

### Add bandwidth, delay and qdisc at interface ###

# TODO: Adding link properties, bandwidth and delay
# to interface, might lead to confusion.

eth_p1r1.set_attributes('100mbit', '5ms')
eth_r1p1.set_attributes('100mbit', '5ms')

eth_p2r2.set_attributes('100mbit', '5ms')
eth_r2p2.set_attributes('100mbit', '5ms')

# Bottleneck link
eth_r1r2.set_attributes('10mbit', '40ms', 'codel')
eth_r2r1.set_attributes('10mbit', '40ms', 'pie')

### Add experiment to run ###

# 'Flow objects' to be added to relevant experiments
flow1 = Flow(peer1, peer2, eth_p2r2.address, 0, 10, 4)

exp1 = Experiment('tcp_4up')
exp1.add_flow(flow1)

### Run the experiment! ###
exp1.run()
