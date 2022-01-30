# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
from nest import config

# This program emulates a point to point network between two hosts `h1` and
# `h2`. Five ping packets are sent from `h1` to `h2`, and the success/failure
# of these packets is reported. It is similar to `point-to-point-1.py` in
# `examples/basic-examples`. This program shows a `config` option in NeST
# for the purpose of logging. Note: we have imported a new package called
# `config` in this program (Line 8 above).

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

# The following line configures the NeST to log at ERROR level. When this
# program is run, it does not print INFO statements on the console as done in
# some of the other examples in NeST. Only errors are printed to the console.
config.set_value("log_level", "ERROR")

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
