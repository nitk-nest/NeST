# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

########################
# SHOULD BE RUN AS ROOT
########################
from nest.topology import *
from nest.experiment import *
from nest.topology.network import Network
from nest.topology.address_helper import AddressHelper

# This program emulates point to point networks that connect two hosts `h1`
# and `h2` via two routers `r1` and `r2`. It is similar to the
# udp-point-to-point-3.py example in `examples/udp`. Instead of
# `ping`, one CoAP flow is configured from `h1` to `h2`. The links between
# `h1` to `r1` and between `r2` to `h2` are edge links.

##############################################################################
#                              Network Topology                              #
#                                                                            #
#      1000mbit, 1ms -->       1000mbit, 1ms -->       1000mbit, 1ms -->     #
# h1 -------------------- r1 -------------------- r2 -------------------- h2 #
#     <-- 1000mbit, 1ms       <-- 1000mbit, 1ms        <-- 1000mbit, 1ms     #
#                                                                            #
##############################################################################

# This program sends 40 CoAP messages through two flows and creates a new
# directory called `coap-point-to-point-3(date-timestamp)_dump`. It contains
# a `README` which provides details about the sub-directories and files
# within this directory.

# Create two hosts `h1` and `h2`, and two routers `r1` and `r2`
h1 = Node("h1")
h2 = Node("h2")
r1 = Router("r1")
r2 = Router("r2")

# Set the IPv4 address for the networks, and not the interfaces.
# We will use the `AddressHelper` later to assign addresses to the interfaces.
n1 = Network("192.168.1.0/24")  # network on the left of `r1`
n2 = Network("192.168.2.0/24")  # network between two routers
n3 = Network("192.168.3.0/24")  # network on the right of `r2`

# Connect `h1` to `r1`, `r1` to `r2`, and then `r2` to `h2`
# `eth1` and `eth2` are the interfaces at `h1` and `h2`, respectively.
# `etr1a` is the first interface at `r1` which connects it with `h1`
# `etr1b` is the second interface at `r1` which connects it with `r2`
# `etr2a` is the first interface at `r2` which connects it with `r1`
# `etr2b` is the second interface at `r2` which connects it with `h2`
(eth1, etr1a) = connect(h1, r1, network=n1)
(etr1b, etr2a) = connect(r1, r2, network=n2)
(etr2b, eth2) = connect(r2, h2, network=n3)

# Assign IPv4 addresses to all the interfaces in the network.
AddressHelper.assign_addresses()

# Set the link attributes: `h1` --> `r1` --> `r2` --> `h2`
eth1.set_attributes("1000mbit", "1ms")  # from `h1` to `r1`
etr1b.set_attributes("1000mbit", "1ms")  # from `r1` to `r2`
etr2b.set_attributes("1000mbit", "1ms")  # from `r2` to `h2`

# Set the link attributes: `h2` --> `r2` --> `r1` --> `h1`
eth2.set_attributes("1000mbit", "1ms")  # from `h2` to `r2`
etr2a.set_attributes("1000mbit", "1ms")  # from `r2` to `r1`
etr1a.set_attributes("1000mbit", "1ms")  # from `r1` to `h1`

# Set default routes in `h1` and `h2`. Additionally, set default routes in
# `r1` and `r2` so that the packets that cannot be forwarded based on the
# entries in their routing table are sent via a default interface.
h1.add_route("DEFAULT", eth1)
h2.add_route("DEFAULT", eth2)
r1.add_route("DEFAULT", etr1b)
r2.add_route("DEFAULT", etr2a)

# Set up an Experiment. This API takes the name of the experiment as a string.
exp = Experiment("coap-point-to-point-3")

# The user options for the flow emulating a GET request.
#
# Here, the timeout is for the `await` call when sending
# a NON request. Since there is no guarantee of ever receiving
# a response for a NON message, there needs to be a timeout period
# after which there is a timeout error if the response hasn't
# arrived.
#
# Setting a very low value for this will lead to an error since
# the timeout period might end between the reception of the
# empty ACK and the actual response for the NON message.
user_options_get = {
    "coap_server_content": "This is the user set content",
    "coap_non_timeout": "5.0",
}

# The user options for the flow emulating a PUT request.
user_options_put = {
    "coap_request_type": "put",
    "coap_message_payload": "This is the new message payload",
}

# These can be configured to set the number of CON and NON
# messages sent in each flow.
n_con_msgs = 10
n_non_msgs = 10

# Configure a flow from `h1` to `h2`. Here, the number of CON and
# NON messages is set to 10 each. The user options defined above are
# provided to the flow as well.
flow_get = CoapFlow(
    h1, h2, eth2.get_address(), n_con_msgs, n_non_msgs, user_options_get
)
flow_put = CoapFlow(
    h1, h2, eth2.get_address(), n_con_msgs, n_non_msgs, user_options_put
)

# Add the above flows as CoAP flows to the current experiment
exp.add_coap_flow(flow_get)
exp.add_coap_flow(flow_put)

# Run the experiment
exp.run()
