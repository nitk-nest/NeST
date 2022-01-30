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
# `examples/basic-examples`. This program shows two `config` options in NeST
# for ease of experimentation. For this purpose, we have imported a new
# package called `config` in this program (Line 8 above).

#################################
#       Network Topology        #
#                               #
#          5mbit, 5ms -->       #
#   h1 ------------------- h2   #
#       <-- 10mbit, 100ms       #
#                               #
#################################

# By default, NeST deletes all the nodes (or network namespaces) at the end of
# the experiment. One of the `config` options in NeST allows the user to
# customize this behavior, if needed, and retain the namespaces. Another
# `config` option in NeST is to avoid giving random names to the namespaces.
# Since NeST allows multiple programs to run in parallel on the same machine,
# it internally assigns random names to the namespaces by default. However,
# when random names are disabled, node names cannot be longer than three
# characters. We use names `h1` and `h2` in this example.

# The following two lines ensure that NeST does not delete namespaces during
# the termination of this experiment, and does not assign random names to the
# namespaces. After running this program, use `ip netns` command to see the
# namespaces created by NeST. IMPORTANT: Do not forget to delete the namespaces
# manually before re-running this program. You can delete namespaces one-by-one
# by using `sudo ip netns del h1` command (similarly for `h2`) or delete all
# namespaces at once by using `sudo ip --all netns del`. Be careful if you
# choose to delete all namespaces because this command will delete all the
# namespaces in your system (even the ones that were not created by NeST).
config.set_value("delete_namespaces_on_termination", False)
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
