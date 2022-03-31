# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *

# This program emulates point to point networks that connect two hosts `h1`
# and `h2` via two routers `r1` and `r2`. Five ping packets are sent from `h1`
# to `h2`, and the success/failure of these packets is reported. It is similar
# to `ipv6-point-to-point-3.py` available in `examples/ipv6`, the only
# difference is that both IPv4 and IPv6 addresses are used simultaneously in
# this program.

##############################################################################
#                              Network Topology                              #
#                                                                            #
#        5mbit, 5ms -->          5mbit, 5ms -->          5mbit, 5ms -->      #
# h1 -------------------- r1 -------------------- r2 -------------------- h2 #
#     <-- 10mbit, 100ms       <-- 10mbit, 100ms       <-- 10mbit, 100ms      #
#                                                                            #
##############################################################################

# Create two hosts `h1` and `h2`, and two routers `r1` and `r2`
h1 = Node("h1")
h2 = Node("h2")
r1 = Router("r1")
r2 = Router("r2")

# Connect `h1` to `r1`, `r1` to `r2`, and then `r2` to `h2`
# `eth1` and `eth2` are the interfaces at `h1` and `h2`, respectively.
# `etr1a` is the first interface at `r1` which connects it with `h1`
# `etr1b` is the second interface at `r1` which connects it with `r2`
# `etr2a` is the first interface at `r2` which connects it with `r1`
# `etr2b` is the second interface at `r2` which connects it with `h2`
(eth1, etr1a) = connect(h1, r1)
(etr1b, etr2a) = connect(r1, r2)
(etr2b, eth2) = connect(r2, h2)

# Assign IPv6 addresses to all the interfaces.
# Note: this example has three networks: one on the left of `r1`, second
# between the two routers, and third on the right of `r2`.
# Assign IPv6 addresses to interfaces in the network which is on the left of
# `r1`. We assume that the IPv6 address of this network is `2001::1/122` and
# IPv4 address is `192.168.1.0/24`
eth1.set_address(["2001::1:1/122", "192.168.1.1/24"])
etr1a.set_address(["2001::1:2/122", "192.168.1.2/24"])

# Assign IPv6 addresses to interfaces in the network which is between the two
# routers. We assume that the IPv6 address of this network is `2001::2/122`
# and IPv4 address is `192.168.2.0/24`
etr1b.set_address(["2001::2:1/122", "192.168.2.1/24"])
etr2a.set_address(["2001::2:2/122", "192.168.2.2/24"])

# Assign IPv6 addresses to interfaces in the network which is on the right of
# `r2`. We assume that the IPv6 address of this network is `2001::3/122` and
# IPv4 address is `192.168.3.0/24`
etr2b.set_address(["2001::3:1/122", "192.168.3.1/24"])
eth2.set_address(["2001::3:2/122", "192.168.3.2/24"])

# Set the link attributes: `h1` --> `r1` --> `r2` --> `h2`
eth1.set_attributes("5mbit", "5ms")  # from `h1` to `r1`
etr1b.set_attributes("5mbit", "5ms")  # from `r1` to `r2`
etr2b.set_attributes("5mbit", "5ms")  # from `r2` to `h2`

# Set the link attributes: `h2` --> `r2` --> `r1` --> `h1`
eth2.set_attributes("10mbit", "100ms")  # from `h2` to `r2`
etr2a.set_attributes("10mbit", "100ms")  # from `r2` to `r1`
etr1a.set_attributes("10mbit", "100ms")  # from `r1` to `h1`

# Set default routes in `h1` and `h2`. Additionally, set default routes in
# `r1` and `r2` so that the packets that cannot be forwarded based on the
# entries in their routing table are sent via next hop addresses specified.
# For IPv4:
h1.add_route("DEFAULT", eth1, eth1.pair.get_address(True, False))
h2.add_route("DEFAULT", eth2, eth2.pair.get_address(True, False))
r1.add_route("DEFAULT", etr1b, etr1b.pair.get_address(True, False))
r2.add_route("DEFAULT", etr2a, etr2a.pair.get_address(True, False))
# For IPv6:
h1.add_route("DEFAULT", eth1, eth1.pair.get_address(False, True))
h2.add_route("DEFAULT", eth2, eth2.pair.get_address(False, True))
r1.add_route("DEFAULT", etr1b, etr1b.pair.get_address(False, True))
r2.add_route("DEFAULT", etr2a, etr2a.pair.get_address(False, True))

# `Ping` from `h1` to `h2`.
h1.ping(eth2.get_address(True, False))  # IPv4
h1.ping(eth2.get_address(False, True))  # IPv6
