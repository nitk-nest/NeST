# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

##############################################################################################
# 																							 #
#                 mpls_encap->              pop                <-mpls_encap                  #
# (c1) ------------ [pe1] ----------------- [p] ------------------ [pe2] -------------- (c2) #
# (1.1.1.1   1.1.1.2) | (11.1.1.1  11.1.1.2) | (22.1.1.2   22.1.1.1) | (2.1.1.2   2.1.1.1)   #
# 																							 #
##############################################################################################

from nest.topology import *
from nest.experiment import *
from nest.routing.routing_helper import RoutingHelper
from nest import config

config.set_value("routing_suite", "frr")

c1 = Node("c1")
pe1 = Node("pe1")
p = Node("p")
pe2 = Node("pe2")
c2 = Node("c2")

(c1_pe1, pe1_c1) = connect(c1, pe1)
(pe1_p, p_pe1) = connect(pe1, p)
(p_pe2, pe2_p) = connect(p, pe2)
(pe2_c2, c2_pe2) = connect(pe2, c2)

c1_pe1.set_address("1.1.1.1/24")
pe1_c1.set_address("1.1.1.2/24")

pe1_p.set_address("11.1.1.1/24")
p_pe1.set_address("11.1.1.2/24")

c2_pe2.set_address("2.1.1.1/24")
pe2_c2.set_address("2.1.1.2/24")

pe2_p.set_address("22.1.1.1/24")
p_pe2.set_address("22.1.1.2/24")

pe1.enable_ip_forwarding()
pe2.enable_ip_forwarding()
p.enable_ip_forwarding()

# Enable mpls in the required interfaces
pe1_p.enable_mpls()
p_pe1.enable_mpls()

pe2_p.enable_mpls()
p_pe2.enable_mpls()


# Dynamic routing using LDP
# Runs ldp on routers with mpls enabled interfaces

RoutingHelper("ospf", ldp_routers=[pe1, p, pe2]).populate_routing_tables()

# As of now, there's no proper way of verifying if all routes from ldp are installed.
# Ensure that ldp daemon gets sufficient time to install routes.
# If ldp routes aren't installed, add a approximate sleep time
#
# from time import sleep
# sleep(10)

c1.ping("2.1.1.1", verbose=True)
c2.ping("1.1.1.1", verbose=True)

flow = Flow(c1, c2, c2_pe2.address, 0, 30, 2)

exp = Experiment("mpls_tcp_flow")
exp.add_tcp_flow(flow)
exp.run()
