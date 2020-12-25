# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# MPLS example
#
# (c1) ------------ [pe1] ----------------- [p] ------------------ [pe2] -------------- (c2)
# (1.1.1.1   1.1.1.2) | (11.1.1.1  11.1.1.2) | (22.1.1.2   22.1.1.1) | (2.1.1.2   2.1.1.1)

from nest.topology import *
from nest.experiment import *

c1 = Node('c1')
pe1 = Node('pe1')
p = Node('p')
pe2 = Node('pe2')
c2 = Node('c2')

(c1_pe1, pe1_c1) = connect(c1, pe1)
(pe1_p, p_pe1) = connect(pe1, p)
(p_pe2, pe2_p) = connect(p, pe2)
(pe2_c2, c2_pe2) = connect(pe2, c2)

c1_pe1.set_address('1.1.1.1/24')
pe1_c1.set_address('1.1.1.2/24')

pe1_p.set_address('11.1.1.1/24')
p_pe1.set_address('11.1.1.2/24')

c2_pe2.set_address('2.1.1.1/24')
pe2_c2.set_address('2.1.1.2/24')

pe2_p.set_address('22.1.1.1/24')
p_pe2.set_address('22.1.1.2/24')

pe1.enable_ip_forwarding()
pe2.enable_ip_forwarding()
p.enable_ip_forwarding()

# Enable mpls in the required interfaces
pe1_p.enable_mpls()
p_pe1.enable_mpls()

pe2_p.enable_mpls()
p_pe2.enable_mpls()


c1.add_route('DEFAULT', c1.interfaces[0])
c2.add_route('DEFAULT', c2.interfaces[0])

# add static routes (mpls family)

# encap the ip packet with mpls (push)
pe1.add_route_mpls_push('2.1.1.0/30', '11.1.1.2', 100)
pe2.add_route_mpls_push('1.1.1.0/30', '22.1.1.2', 200)

# pop the label and forward the ip packet
p.add_route_mpls_pop(100, '22.1.1.1')
p.add_route_mpls_pop(200, '11.1.1.1')

c1.ping('2.1.1.1', verbose=True)
c2.ping('1.1.1.1', verbose=True)

flow = Flow(c1, c2, c2_pe2.address, 0, 10, 2)

exp = Experiment('mpls_tcp_flow')
exp.add_tcp_flow(flow)
exp.run()
