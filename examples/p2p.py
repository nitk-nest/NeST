# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
import sys

sys.path.append('../')

from nest.topology import *
from nest.test import *

##############################
# Topology
#
# n0 ----- n1
##############################

n0 = Node('n0')
n1 = Node('n1')

(n0_n1, n1_n0) = connect(n0, n1)

n0_n1.set_address('10.0.0.1/24')
n1_n0.set_address('10.0.0.2/24')

n0_n1.set_attributes('5mbit', '5ms', 'pfifo')

test = Test('tcp_1up')
test.add_flow(Flow(n0, n1, n1_n0.get_address(), 0, 10, 1))

test.run()