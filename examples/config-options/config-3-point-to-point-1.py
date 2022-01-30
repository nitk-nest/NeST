# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
from nest import config
import os
from pathlib import Path

# This program emulates a point to point network between two hosts `h1` and
# `h2`. Five ping packets are sent from `h1` to `h2`, and the success/failure
# of these packets is reported. It is similar to `point-to-point-1.py` in
# `examples/basic-examples`. This program shows a `config` option in NeST to
# import custom configuration from a JSON file. This option overwrites the
# default values in NeST for the parameters that are specified in the JSON
# file. The default values of other parameters are not overwritten. Note: we
# have imported a new package called `config` in this program (Line 8 above).

#################################
#       Network Topology        #
#                               #
#          5mbit, 5ms -->       #
#   h1 ------------------- h2   #
#       <-- 10mbit, 100ms       #
#                               #
#################################

# The following lines enable NeST to read the configuration from the file
# named `custom-config.json` which is placed in the same directory as this
# program. ALTERNATIVE: If you prefer to import custom configuration without
# using the two lines shown below, name the JSON file as `nest-config.json`
# and keep it in the same directory as this program, or in /etc, or ~/.
# In this example, `custom-config.json` changes the default values of
# `assign_random_names` and `delete_namespaces_on_termination`, and changes the
# `log_level` to `ERROR`.
# IMPORTANT: Do not forget to delete the namespaces after running this program.
CONFIG_DIR = Path(os.path.abspath(__file__)).parent
config.import_custom_config(CONFIG_DIR / "custom-config.json")

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
