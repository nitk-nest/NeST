from nest import config
from nest.experiment import *
from nest.routing.routing_helper import RoutingHelper
from nest.topology import *

peer1 = Node("peer-1")
peer2 = Node("peer-2")
router1 = Node("router-1")
router2 = Node("router-2")


router1.enable_ip_forwarding()
router2.enable_ip_forwarding()

(eth_p1r1, eth_r1p1) = connect(peer1, router1, "eth-p1r1-0", "eth-r1p1-0")
(eth_r1r2, eth_r2r1) = connect(router1, router2, "eth-r1r2-0", "eth-r2r1-0")
(eth_r2p2, eth_p2r2) = connect(router2, peer2, "eth-r2p2-0", "eth-p2r2-0")


eth_p1r1.set_address("10.0.1.1/24")
eth_r1p1.set_address("10.0.1.2/24")
eth_r1r2.set_address("10.0.2.2/24")
eth_r2r1.set_address("10.0.2.3/24")
eth_r2p2.set_address("10.0.3.3/24")
eth_p2r2.set_address("10.0.3.4/24")
config.set_value("routing_suite", "bird")
RoutingHelper(protocol="rip").populate_routing_tables()

flow1 = Flow(peer1, peer2, eth_p2r2.address, 0, 10, 4)
exp1 = Experiment("tcp_4up")
exp1.add_flow(flow1)

exp1.run()
