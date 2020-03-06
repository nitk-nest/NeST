# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT#
########################
import sys

sys.path.append('../')
from nest.topology import *


##############################
# Topology
#
# n1 -->-- r1 -->-- n2 
##############################

n2 = Node('n2')
r = Router('r')
n1 = Node('n1')

n1.add_stats_to_plot('cwnd')

r.add_stats_to_plot('qlen')

(n1_r, r_n1) = connect(n1, r)
(r_n2, n2_r) = connect(r, n2)

n1_r.set_address('10.1.1.1/24')
r_n1.set_address('10.1.1.2/24')
r_n2.set_address('10.1.2.1/24')
n2_r.set_address('10.1.2.2/24')

n1.add_route('DEFAULT', '10.1.1.2', n1_r)
n2.add_route('DEFAULT', '10.1.2.1', n2_r)

n2.install_server()
n1.send_packets_to('10.1.2.2')
Configuration.generate_config_file(filename='PRP2')

