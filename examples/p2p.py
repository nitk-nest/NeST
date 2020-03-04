# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
import sys

sys.path.append('../')

from nest import *

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

n0_n1.set_min_bandwidth(5)  # mbit
n0_n1.set_delay(200)        # ms
n0_n1.set_qdisc('pfifo')

# n0_n1.add_qdisc('htb', 'root', '1:', default = '12')
# n0_n1.add_class('htb', '1:', '1:1', rate = '100kbps', ceil = '100kbps', burst = '2k')
# n0_n1.add_class('htb', '1:1', '1:10', rate = '30kbps', ceil = '100kbps', burst = '2k')
# n0_n1.add_class('htb', '1:1', '1:11', rate = '10kbps', ceil = '100kbps', burst = '2k')
# n0_n1.add_class('htb', '1:1', '1:12', rate = '60kbps', ceil = '100kbps', burst = '2k')

# Application layer

n1.install_server()
n0.send_packets_to('10.0.0.1')

# Generate config file at the end of topology
# TODO: Think of a better approach

Configuration.generate_config_file()