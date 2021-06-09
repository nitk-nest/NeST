# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.experiment import *
from nest.topology import *
import subprocess

# This program emulates the following topology:
#
#            1000 Mbps           10Mbps          1000 Mbps
#   Sender -------------- R1 -------------- R2 -------------- Receiver
#               5ms               10ms               5ms
#
#  The link between R1 and R2 is a bottleneck link with 10 Mbps. All other
#  links are 1000 Mbps.

# Create Nodes
sender = Node("sender")
receiver = Node("receiver")
router1 = Node("router1")
router2 = Node("router2")

# Enable IP forwarding in routers
router1.enable_ip_forwarding()
router2.enable_ip_forwarding()

# Create interfaces and connect nodes and routers
(sender_router1, router1_sender) = connect(sender, router1)
(router1_router2, router2_router1) = connect(router1, router2)
(router2_receiver, receiver_router2) = connect(router2, receiver)

# Assign addresses to interfaces
sender_router1.set_address("10.0.1.1/24")
router1_sender.set_address("10.0.1.2/24")

router1_router2.set_address("10.0.2.2/24")
router2_router1.set_address("10.0.2.3/24")

router2_receiver.set_address("10.0.3.3/24")
receiver_router2.set_address("10.0.3.4/24")

# Set default routes
sender.add_route("DEFAULT", sender_router1)
receiver.add_route("DEFAULT", receiver_router2)

router1.add_route("DEFAULT", router1_router2)
router2.add_route("DEFAULT", router2_router1)

# Configure the queue discipline and set its capacity to 100 packets
qdisc = "pfifo"
qdisc_parameters = {"limit": "100"}

# Configure bandwidth, delay and qdisc attributes
# Sender edge
sender_router1.set_attributes("1000mbit", "5ms")
router1_sender.set_attributes("1000mbit", "5ms")

# Receiver edge
receiver_router2.set_attributes("1000mbit", "5ms")
router2_receiver.set_attributes("1000mbit", "5ms")

# Bottleneck link
router1_router2.set_attributes("10mbit", "10ms", qdisc, **qdisc_parameters)
router2_router1.set_attributes("10mbit", "10ms", qdisc, **qdisc_parameters)

# Disable offloads
offload_type = ["gso", "gro", "tso"]
sender_router1.disable_offload(offload_type)
router1_router2.disable_offload(offload_type)
router2_router1.disable_offload(offload_type)
receiver_router2.disable_offload(offload_type)

# Create one flow from sender to receiver for 100 seconds
flow = Flow(sender, receiver, receiver_router2.get_address(), 0, 100, 1)

# Configure the experiment: give a name and set the TCP variant
exp = Experiment("BBR_validation")
exp.add_tcp_flow(flow, "bbr")

# Collect statistics from the queue discipline
exp.require_qdisc_stats(router1_router2)

# Run the experiment
exp.run()
