# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
import sys

sys.path.append('../')

from nest.topology import *
from nest.experiment import *

#############################################
# This is an implementation of gfc-1 topology
# GFC Topology:
#                      d2      f2      a2    c2      e2
#                       \       \       \    /       /
#                        \       \       \  /       /
#                         \       \       \/       /
#         a1------r1------r2------r3------r4------r5------b2
#                 /       /\       \       \
#                /       /  \       \       \
#               /       /    \       \       \
#              d1      b1    f1      c1      e1
#############################################

a1 = Node('a1')
b1 = Node('b1')
c1 = Node('c1')
d1 = Node('d1')
e1 = Node('e1')
f1 = Node('f1')

r1 = Node('r1')
r2 = Node('r2')
r3 = Node('r3')
r4 = Node('r4')
r5 = Node('r5')

a2 = Node('a2')
b2 = Node('b2')
c2 = Node('c2')
d2 = Node('d2')
e2 = Node('e2')
f2 = Node('f2')

(r1_a1, a1_r1) = connect(r1, a1)
(r2_b1, b1_r2) = connect(r2, b1)
(r1_d1, d1_r1) = connect(r1, d1)
(r2_f1, f1_r2) = connect(r2, f1)
(r3_c1, c1_r3) = connect(r3, c1)
(r4_e1, e1_r4) = connect(r4, e1)
(r2_r1, r1_r2) = connect(r2, r1)
(r3_r2, r2_r3) = connect(r3, r2)
(r4_r3, r3_r4) = connect(r4, r3)
(r5_r4, r4_r5) = connect(r5, r4)
(r4_a2, a2_r4) = connect(r4, a2)
(r5_b2, b2_r5) = connect(r5, b2)
(r2_d2, d2_r2) = connect(r2, d2)
(r3_f2, f2_r3) = connect(r3, f2)
(r4_c2, c2_r4) = connect(r4, c2)
(r5_e2, e2_r5) = connect(r5, e2)

a1_r1.set_address('10.0.1.1/24')
a2_r4.set_address('10.0.6.6/24')
b1_r2.set_address('10.0.11.1/24')
b2_r5.set_address('10.0.18.5/24')
d1_r1.set_address('10.0.9.1/24')
d2_r2.set_address('10.0.10.1/24')
f1_r2.set_address('10.0.12.1/24')
f2_r3.set_address('10.0.13.1/24')
c1_r3.set_address('10.0.14.1/24')
c2_r4.set_address('10.0.15.2/24')
e1_r4.set_address('10.0.16.3/24')
e2_r5.set_address('10.0.17.5/24')
r2_d2.set_address('10.0.10.3/24')
r1_a1.set_address('10.0.1.2/24')
r1_d1.set_address('10.0.9.2/24')
r1_r2.set_address('10.0.2.2/24')
r2_b1.set_address('10.0.11.3/24')
r2_r1.set_address('10.0.2.3/24')
r2_r3.set_address('10.0.3.3/24')
r2_f1.set_address('10.0.12.3/24')
r3_r2.set_address('10.0.3.4/24')
r3_r4.set_address('10.0.4.4/24')
r3_f2.set_address('10.0.13.4/24')
r3_c1.set_address('10.0.14.4/24')
r4_a2.set_address('10.0.6.5/24')
r4_c2.set_address('10.0.15.5/24')
r4_r3.set_address('10.0.4.5/24')
r4_r5.set_address('10.0.5.5/24')
r4_e1.set_address('10.0.16.5/24')
r5_r4.set_address('10.0.5.6/24')
r5_b2.set_address('10.0.18.6/24')
r5_e2.set_address('10.0.17.6/24')

a1.add_route('DEFAULT', a1_r1)
a2.add_route('DEFAULT', a2_r4)
r5.add_route('DEFAULT', r5_r4)

r1.add_route('DEFAULT', r1_r2)
r2.add_route('DEFAULT', r2_r3)
r4.add_route('DEFAULT', r4_r5)

b1.add_route('DEFAULT', b1_r2)
b2.add_route('DEFAULT', b2_r5)
r4.add_route('10.0.18.0/24', r4_r5)
r3.add_route('10.0.11.0/24', r3_r2)
r3.add_route('10.0.18.0/24', r3_r4)
r4.add_route('10.0.11.0/24', r4_r3)

d1.add_route('DEFAULT', d1_r1)
d2.add_route('DEFAULT', d2_r2)
r2.add_route('10.0.9.0/24', r2_r1)
r1.add_route('10.0.10.0/24', r1_r2)

f1.add_route('DEFAULT', f1_r2)
f2.add_route('DEFAULT', f2_r3)
r2.add_route('10.0.13.0/24', r2_r3)
r3.add_route('10.0.12.0/24', r3_r2)

c1.add_route('DEFAULT', c1_r3)
c2.add_route('DEFAULT', c2_r4)
r3.add_route('10.0.15.0/24', r3_r4)
r4.add_route('10.0.14.0/24', r4_r3)

e1.add_route('DEFAULT', e1_r4)
e2.add_route('DEFAULT', e2_r5)
r4.add_route('10.0.17.0/24', r4_r5)
r5.add_route('10.0.16.0/24', r5_r4)

r2.add_route('10.0.6.0/24', r2_r3)
r3.add_route('10.0.5.0/24', r3_r4)
r3.add_route('10.0.6.0/24', r3_r4)
r4.add_route('10.0.1.0/24', r4_r3)
r3.add_route('10.0.1.0/24', r3_r2)
r2.add_route('10.0.2.0/24', r3_r2)
r2.add_route('10.0.1.0/24', r2_r1)

# node_router_bandwidth = input('Enter the link access bandwidth')
# print(node_router_bandwidth)

# r1_r2_bandwidth = input('Enter the bandwidth between router r1 and r2')

# r2_r3_bandwidth = input('Enter the bandwidth between router r2 and r3')

# r3_r4_bandwidth = input('Enter the bandwidth between router r3 and r4')

# r4_r5_bandwidth = input('Enter the bandwidth between router r4 and r5')

# qdisc = input('Enter the Queueing algorithm for the nodes')

sample_bandwidth = '50'
sample_delay = '100'
sample_qdisc = 'pfifo'

a1_r1.set_attributes(sample_bandwidth, sample_delay)
r1_a1.set_attributes(sample_bandwidth, sample_delay)

b1_r2.set_attributes(sample_bandwidth, sample_delay)
r2_b1.set_attributes(sample_bandwidth, sample_delay)

d1_r1.set_attributes(sample_bandwidth, sample_delay)
r1_d1.set_attributes(sample_bandwidth, sample_delay)

f1_r2.set_attributes(sample_bandwidth, sample_delay)
r2_f1.set_attributes(sample_bandwidth, sample_delay)

c1_r3.set_attributes(sample_bandwidth, sample_delay)
r3_c1.set_attributes(sample_bandwidth, sample_delay)

e1_r4.set_attributes(sample_bandwidth, sample_delay)
r4_e1.set_attributes(sample_bandwidth, sample_delay)

qdisc_args = {
    'ce_threshold' : '1.6ms',
    'limit' : '1000',
    'target' : '100ms',
    'ecn' : ''
}
r1_r2.set_attributes(sample_bandwidth, sample_delay, 'pfifo', **qdisc_args)
r2_r1.set_attributes(sample_bandwidth, sample_delay, 'pfifo')
r2_r3.set_attributes(sample_bandwidth, sample_delay, 'pfifo', **qdisc_args)
r3_r2.set_attributes(sample_bandwidth, sample_delay, 'pfifo')
r3_r4.set_attributes(sample_bandwidth, sample_delay, 'pfifo', **qdisc_args)
r4_r3.set_attributes(sample_bandwidth, sample_delay, 'pfifo')
r4_r5.set_attributes(sample_bandwidth, sample_delay, 'pfifo', **qdisc_args)
r5_r4.set_attributes(sample_bandwidth, sample_delay, 'pfifo')
e2_r5.set_attributes(sample_bandwidth, sample_delay, 'pfifo')
r5_e2.set_attributes(sample_bandwidth, sample_delay, 'pfifo')
c2_r4.set_attributes(sample_bandwidth, sample_delay, 'pfifo')
r4_c2.set_attributes(sample_bandwidth, sample_delay, 'pfifo')
f2_r3.set_attributes(sample_bandwidth, sample_delay, 'pfifo')
r3_f2.set_attributes(sample_bandwidth, sample_delay, 'pfifo')
d2_r2.set_attributes(sample_bandwidth, sample_delay, 'pfifo')
r2_d2.set_attributes(sample_bandwidth, sample_delay, 'pfifo')
b2_r5.set_attributes(sample_bandwidth, sample_delay, 'pfifo')
r5_b2.set_attributes(sample_bandwidth, sample_delay, 'pfifo')
a2_r4.set_attributes(sample_bandwidth, sample_delay, 'pfifo')
r4_a2.set_attributes(sample_bandwidth, sample_delay, 'pfifo')