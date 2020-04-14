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
a2 = Node('a2')
a3 = Node('a3')
a11 = Node('a11')

b1 = Node('b1')
b2 = Node('b2')
b3 = Node('b3')
b11 = Node('b11')

c1 = Node('c1')
c2 = Node('c2')

d1 = Node('d1')
d2 = Node('d2')

e1 = Node('e1')
e2 = Node('e2')

f1 = Node('f1')
f2 = Node('f2')

g1 = Node('g1')
g2 = Node('g2')

h1 = Node('h1')
h2 = Node('h2')

r1 = Node('r1')
r2 = Node('r2')
r3 = Node('r3')
r4 = Node('r4')
r5 = Node('r5')
r6 = Node('r6')
r7 = Node('r7')

(r1_a1, a1_r1) = connect(r1, a1)
(r1_b1, b1_r1) = connect(r1, b1)
(r1_d1, d1_r1) = connect(r1, d1)
(r2_e1, e1_r2) = connect(r2, e1)
(r2_a2, a2_r2) = connect(r2, a2)
(r2_b2, b2_r2) = connect(r2, b2)
(r3_a3, a3_r3) = connect(r3, a3)
(r3_f1, f1_r3) = connect(r3, f1)
(r4_b3, b3_r4) = connect(r4, b3)
(r4_h1, h1_r4) = connect(r4, h1)
(r5_c1, c1_r5) = connect(r5, c1)
(r6_g1, g1_r6) = connect(r6, g1)

(r2_r1, r1_r2) = connect(r2, r1)
(r3_r2, r2_r3) = connect(r3, r2)
(r4_r3, r3_r4) = connect(r4, r3)
(r5_r4, r4_r5) = connect(r5, r4)
(r6_r5, r5_r6) = connect(r6, r5)
(r7_r6, r6_r7) = connect(r7, r6)

(r2_d2, d2_r2) = connect(r2, d2)
(r3_e2, e2_r3) = connect(r3, e2)
(r4_f2, f2_r4) = connect(r4, f2)
(r5_h2, h2_r5) = connect(r5, h2)
(r6_c2, c2_r6) = connect(r6, c2)
(r6_a11, a11_r6) = connect(r6, a11)
(r7_b11, b11_r7) = connect(r7, b11)
(r7_g2, g2_r7) = connect(r7, g2)

a1_r1.set_address('10.0.1.1/24')
a2_r2.set_address('10.0.6.1/24')
a3_r3.set_address('10.0.8.1/24')
a11_r6.set_address('10.0.24.9/24')
b1_r1.set_address('10.0.2.1/24')
b2_r2.set_address('10.0.5.1/24')
b3_r4.set_address('10.0.11.1/24')
b11_r7.set_address('10.0.20.9/24')
d1_r1.set_address('10.0.3.1/24')
d2_r2.set_address('10.0.30.9/24')
f1_r3.set_address('10.0.9.1/24')
f2_r4.set_address('10.0.28.9/24')
c1_r5.set_address('10.0.14.1/24')
c2_r6.set_address('10.0.23.9/24')
e1_r2.set_address('10.0.18.1/24')
e2_r3.set_address('10.0.29.9/24')
g1_r6.set_address('10.0.17.1/24')
g2_r7.set_address('10.0.19.9/24')
h1_r4.set_address('10.0.12.1/24')
h2_r5.set_address('10.0.27.9/24')

r1_a1.set_address('10.0.1.2/24')
r1_d1.set_address('10.0.3.2/24')
r1_b1.set_address('10.0.2.2/24')
r1_r2.set_address('10.0.4.2/24')
r2_b2.set_address('10.0.5.3/24')
r2_r1.set_address('10.0.4.3/24')
r2_r3.set_address('10.0.7.3/24')
r2_d2.set_address('10.0.30.3/24')
r2_a2.set_address('10.0.6.3/24')
r2_e1.set_address('10.0.18.3/24')
r3_r2.set_address('10.0.7.4/24')
r3_r4.set_address('10.0.10.4/24')
r3_f1.set_address('10.0.9.4/24')
r3_a3.set_address('10.0.8.4/24')
r3_e2.set_address('10.0.29.4/24')
r4_f2.set_address('10.0.28.5/24')
r4_b3.set_address('10.0.11.5/24')
r4_r3.set_address('10.0.10.5/24')
r4_r5.set_address('10.0.13.5/24')
r4_h1.set_address('10.0.12.5/24')
r5_r4.set_address('10.0.13.6/24')
r5_r6.set_address('10.0.16.6/24')
r5_c1.set_address('10.0.14.6/24')
r5_h2.set_address('10.0.27.6/24')
r6_c2.set_address('10.0.23.7/24')
r6_r5.set_address('10.0.16.7/24')
r6_r7.set_address('10.0.18.7/24')
r6_g1.set_address('10.0.17.7/24')
r6_a11.set_address('10.0.24.7/24')
r7_g2.set_address('10.0.19.8/24')
r7_r6.set_address('10.0.18.8/24')
r7_b11.set_address('10.0.20.8/24')

a2_r2.set_address('10.0.6.3')
a3_r3.set_address('10.0.8.4')
a11_r6.set_address('10.0.24.7')

b2_r2.set_address('10.0.5.3')
b3_r4.set_address('10.0.11.5')
d2_r2.set_address('10.0.30.3')
f1_r3.set_address('10.0.9.4')
f2_r4.set_address('10.0.28.5')
c1_r5.set_address('10.0.14.6')
c2_r6.set_address('10.0.23.7')
e1_r2.set_address('10.0.18.3')
e2_r3.set_address('10.0.29.4')
g2_r7.set_address('10.0.19.8')
h1_r4.set_address('10.0.12.5')
h2_r5.set_address('10.0.27.6')
a1_r1.set_address('10.0.1.2')
b1_r1.set_address('10.0.2.2')
b11_r7.set_address('10.0.20.8')
d1_r1.set_address('10.0.3.2')
g1_r6.set_address('10.0.17.7')

r1.add_route('10.0.30.0/24', r1_r2)
r1.add_route('DEFAULT', r1_r2)
r2.add_route('0.0.3.0/24', r2_r1)
r2.add_route('0.0.1.0/24', r2_r1)
r2.add_route('0.0.2.0/24', r2_r1)

r2.add_route('10.0.24.0/24', r2_r3)
r2.add_route('10.0.20.0/24', r2_r3)
r2.add_route('10.0.29.0/24', r2_r3)
r2.add_route('10.0.18.0/24', r2_r3)
r3.add_route('10.0.6.0/24', r3_r2)
r3.add_route('10.0.5.0/24', r3_r2)
r3.add_route('10.0.1.0/24', r3_r2)
r3.add_route('10.0.2.0/24', r3_r2)

r3.add_route('10.0.24.0/24', r3_r4)
r3.add_route('10.0.20.0/24', r3_r4)
r3.add_route('10.0.28.0/24', r3_r4)
r4.add_route('10.0.9.0/24', r4_r3)

r4.add_route('10.0.1.0/24', r4_r3)
r4.add_route('10.0.2.0/24', r4_r3)
r4.add_route('10.0.5.0/24', r4_r3)
r4.add_route('10.0.6.0/24', r4_r3)
r4.add_route('10.0.8.0/24', r4_r3)

r4.add_route('10.0.24.0/24', r4_r5)
r4.add_route('10.0.20.0/24', r4_r5)
r4.add_route('10.0.27.0/24', r4_r5)

r5.add_route('10.0.12.0/24', r5_r4)
r5.add_route('10.0.1.0/24', r5_r4)
r5.add_route('10.0.2.0/24', r5_r4)
r5.add_route('10.0.8.0/24', r5_r4)
r5.add_route('10.0.6.0/24', r5_r4)
r5.add_route('10.0.5.0/24', r5_r4)
r5.add_route('10.0.11.0/24', r5_r4)

r5.add_route('10.0.23.0/24', r5_r6)
r5.add_route('10.0.24.0/24', r5_r6)
r5.add_route('10.0.20.0/24', r5_r6)

r6.add_route('10.0.14.0/24', r6_r5)
r6.add_route('10.0.1.0/24', r6_r5)
r6.add_route('10.0.2.0/24', r6_r5)
r6.add_route('10.0.8.0/24', r6_r5)
r6.add_route('10.0.6.0/24', r6_r5)
r6.add_route('10.0.5.0/24', r6_r5)
r6.add_route('10.0.11.0/24', r6_r5)

r6.add_route('10.0.20.0/24', r6_r7)
r6.add_route('10.0.19.0/24', r6_r7)
r7.add_route('10.0.17.0/24', r7_r6)
r7.add_route('10.0.2.0/24', r7_r6)
r7.add_route('10.0.5.0/24', r7_r6)
r7.add_route('10.0.11.0/24', r7_r6)