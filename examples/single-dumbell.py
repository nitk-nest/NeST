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
#
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

### Routing ###

peer1.add_route('DEFAULT', eth_p1r1)
peer2.add_route('DEFAULT', eth_p2r2)

router1.add_route('DEFAULT', eth_r1r2)
router2.add_route('DEFAULT', eth_r2r1)

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
flow1 = Flow(peer1, peer2, eth_p2r2.get_address(), 0, 10, 4)
flow2 = Flow(peer2, peer1, eth_p1r1.get_address(), 0, 10, 4)

# First experiment
exp1 = Experiment('tcp_4up')
exp1.add_flow(flow1)
exp1.require_qdisc_stats(eth_r1r2)
exp1.require_qdisc_stats(eth_r2r1)

# Second experiment
exp2 = Experiment('tcp_4down')
exp2.add_flow(flow2)
exp2.require_qdisc_stats(eth_r2r1)

# Third experiment
exp3 = Experiment('tcp_4up&down')
exp3.add_flow(flow1)
exp3.add_flow(flow2)

### Run the experiment! ###

# Run these experiments sequentially; seperately
exp1.run()

# TODO: Running multiple experiments haven't been
# tested properly yet
# TODO: Running to multiple flows in a experiment
# is leading to unexpected behaviour. These needs
# to be looked at closely

# exp2.run()
# exp3.run()
