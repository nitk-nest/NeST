# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
from nest import config

# This program emulates a point to point network between two hosts `h1` and
# `h2`. Five ping packets are sent from `h1` to `h2`, and the success/failure
# of these packets is reported. It is similar to `config-2-point-to-point-1.py`
# example. This program shows a `config` option for the purpose of tracing
# internal Linux commands (for example, those of iproute2) executed by NeST.
# Note: we have imported a new package called `config` in this program (Line 8
# above).

#################################
#       Network Topology        #
#                               #
#          5mbit, 5ms -->       #
#   h1 ------------------- h2   #
#       <-- 10mbit, 100ms       #
#                               #
#################################

# NeST supports different levels of logging by using Python's logging levels.
# By default, the logging is enabled at INFO level. Other levels supported are:
# NOTSET, TRACE, DEBUG, WARNING, ERROR and CRITICAL.

# The following line configures the NeST to log at TRACE level. When this
# program is run, it create a file called `commands.sh` with all the iproute2
# commands NeST internally executes.
config.set_value("log_level", "TRACE")

# By default, NeST assigns random names to the network namespaces. Hence, when
# TRACE level log is enabled, the names of network namespaces visible in
# `commands.sh` would be random, and not user-friendly. To make the names look
# user-friendly, disable random name assignment in NeST.
config.set_value("assign_random_names", False)

# Create two hosts `h1` and `h2`.
h1 = Node("h1")
h2 = Node("h2")

# Connect the above two hosts using a veth (virtual Ethernet) pair.
(eth1, eth2) = connect(h1, h2)

# Assign IPv4 address to both the interfaces.
# We assume that the IPv4 address of this network is `192.168.1.0/24`.
eth1.set_address("192.168.1.1/24")
eth2.set_address("192.168.1.2/24")

# Set the link attributes: `h1` --> `h2` and `h2` --> `h1`
eth1.set_attributes("5mbit", "5ms")
eth2.set_attributes("10mbit", "100ms")

# `Ping` from `h1` to `h2`.
h1.ping(eth2.address)
