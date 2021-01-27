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
#   n1 --- r1 --- r2 --- n2
#
################################################

### Set log level ###

# logging.set_log_level(2)

### Create Nodes ###
n1 = Node("n1")
n2 = Node("n2")
r1 = Node("r1")
r2 = Node("r2")

### Enable IP forwarding in routers ###
r1.enable_ip_forwarding()
r2.enable_ip_forwarding()

# Create interfaces and connect nodes and routers
(n1_r1, r1_n1) = connect(n1, r1)
(r1_r2, r2_r1) = connect(r1, r2)
(r2_n2, n2_r2) = connect(r2, n2)

# Assign addresses to interfaces
n1_r1.set_address("10.0.1.1/24")
r1_n1.set_address("10.0.1.2/24")

r1_r2.set_address("10.0.2.2/24")
r2_r1.set_address("10.0.2.3/24")

r2_n2.set_address("10.0.3.3/24")
n2_r2.set_address("10.0.3.4/24")

# Routing
n1.add_route("DEFAULT", n1_r1)
n2.add_route("DEFAULT", n2_r2)

r1.add_route("DEFAULT", r1_r2)
r2.add_route("DEFAULT", r2_r1)

# Add bandwidth, delay and qdisc at interface
n1_r1.set_attributes("100mbit", "5ms")
r1_n1.set_attributes("100mbit", "5ms")

n2_r2.set_attributes("100mbit", "5ms")
r2_n2.set_attributes("100mbit", "5ms")

# Bottleneck link
r1_r2.set_attributes("10mbit", "40ms", "codel")
r2_r1.set_attributes("10mbit", "40ms", "pie")

### Add experiment to run ###

# 'Flow objects' to be added to relevant experiments
flow1 = Flow(n1, n2, n2_r2.get_address(), 0, 10, 4)
flow2 = Flow(n2, n1, n1_r1.get_address(), 0, 10, 4)

# First experiment
exp1 = Experiment("tcp_4up")
exp1.add_flow(flow1)
exp1.require_qdisc_stats(r1_r2)
exp1.require_qdisc_stats(r2_r1)

# Second experiment
exp2 = Experiment("tcp_4down")
exp2.add_flow(flow2)
exp2.require_qdisc_stats(r2_r1)

# Third experiment
exp3 = Experiment("tcp_4up&down")
exp3.add_flow(flow1)
exp3.add_flow(flow2)

# Run these experiments sequentially; separately
exp1.run()
exp2.run()
exp3.run()
