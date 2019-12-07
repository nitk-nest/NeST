# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019 NITK Surathkal

import nest

##############################
#
# Topology:
#
# n0 -- r0 -- r1 -- r2 -- n1
#
##############################

###### TOPOLOGY CREATION ######

# Create nodes
n0 = Node()
n1 = Node()

# Create routers
r0 = Router()
r1 = Router()
r2 = Router()

# Add connections
(n0_r0, r0_n0) = connect(n0, r0)
(r0_r1, r1_r0) = connect(r0, r1)
(r1_r2, r2_r1) = connect(r1, r2)
(r2_n1, n1_r2) = connect(r2, n1)

###### ADDRESS ASSIGNMENT; ROUTE ######

# Assign address
n0_r0.set_address(Address('10.0.0.1/24'))
r0_n0.set_address(Address('10.0.0.2/24'))
r0_r1.set_address(Address('10.0.1.1/24'))
r1_r0.set_address(Address('10.0.1.2/24'))
r1_r2.set_address(Address('10.0.2.1/24'))
r2_r2.set_address(Address('10.0.2.2/24'))
r2_n1.set_address(Address('10.0.3.1/24'))
n1_r2.set_address(Address('10.0.3.2/24'))

# Add routes
n0.add_route(Address('DEFAULT'), Address('10.0.0.2'), r0_n0) # ip route add default via 10.0.0.2 dev r0_n0
r1.add_route(Address('DEFAULT'), Address('10.0.0.1'), n0_r0)
r1.add_route(Address('10.0.3.2'), Address('10.0.1.2'), r0_r1)
# and other routes...
