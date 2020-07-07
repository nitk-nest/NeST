# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
import sys

sys.path.append('../')
from nest.topology import *


##############################
#
# Topology:
#
# n0 -- r0 -- r1 -- n1
#
##############################

###### TOPOLOGY CREATION ######

# Create nodes
n0 = Node('n0')
n1 = Node('n1')

# Create routers
r0 = Router('r0')
r1 = Router('r1')

print('Node and router created')

# Add connections
(n0_r0, r0_n0) = connect(n0, r0)
(r0_r1, r1_r0) = connect(r0, r1)
(r1_n1, n1_r1) = connect(r1, n1)

print('Connections made')

###### ADDRESS ASSIGNMENT; ROUTE ######

Address('10.0.0.4/24')
# Assign address
n0_r0.set_address(Address('10.0.0.1/24'))
r0_n0.set_address(Address('10.0.0.2/24'))
r0_r1.set_address(Address('10.0.1.1/24'))
r1_r0.set_address(Address('10.0.1.2/24'))
r1_n1.set_address(Address('10.0.2.1/24'))
n1_r1.set_address(Address('10.0.2.2/24'))

print('Addresses are assigned')

# engine.exec_subprocess('ip -all netns del')
# # TODO: Temporary cleanup routine.
# Replace with more robust stuff

# Add routes
n0.add_route('10.0.2.2', n0_r0)
r0.add_route('10.0.2.2', r0_r1)

print('Routing completed')

# n0_r0_htb = Qdisc(n0_r0, 'htb', 'root', '1:')
########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
import sys

sys.path.append('../')


##############################
#
# Topology:
#
# n0 -- r0 -- r1 -- n1
#
##############################

###### TOPOLOGY CREATION ######

# Create nodes
n0 = Node('n0')
n1 = Node('n1')

# Create routers
r0 = Router('r0')
r1 = Router('r1')

print('Node and router created')

# Add connections
(n0_r0, r0_n0) = connect(n0, r0)
(r0_r1, r1_r0) = connect(r0, r1)
(r1_n1, n1_r1) = connect(r1, n1)

print('Connections made')

###### ADDRESS ASSIGNMENT; ROUTE ######

Address('10.0.0.4/24')
# Assign address
n0_r0.set_address(Address('10.0.0.1/24'))
r0_n0.set_address(Address('10.0.0.2/24'))
r0_r1.set_address(Address('10.0.1.1/24'))
r1_r0.set_address(Address('10.0.1.2/24'))
r1_n1.set_address(Address('10.0.2.1/24'))
n1_r1.set_address(Address('10.0.2.2/24'))

print('Addresses are assigned')

# engine.exec_subprocess('ip -all netns del')
# # TODO: Temporary cleanup routine.
# Replace with more robust stuff

# Add routes
n0.add_route('10.0.2.2', n0_r0)
r0.add_route('10.0.2.2', r0_r1)

print('Routing completed')

# n0_r0_htb = Qdisc(n0_r0, 'htb', 'root', '1:')
