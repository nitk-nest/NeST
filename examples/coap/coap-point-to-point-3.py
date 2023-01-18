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
# `udp-point-to-point-3.py` example in `examples/udp`. Instead of a UDP flow,
# two CoAP applications are configured from `h1` to `h2`, one for sending the GET
# requests and another for sending the PUT requests. `h1` acts as a CoAP client
# and `h2` acts as a CoAP server. Address helper is used in this program to
# assign IPv4 addresses.

##############################################################################
#                              Network Topology                              #
#                                                                            #
#      1000mbit, 1ms -->       1000mbit, 1ms -->       1000mbit, 1ms -->     #
# h1 -------------------- r1 -------------------- r2 -------------------- h2 #
#     <-- 1000mbit, 1ms       <-- 1000mbit, 1ms        <-- 1000mbit, 1ms     #
#                                                                            #
##############################################################################

# This program sends a total of 40 CoAP messages: 20 are GET requests and 20
# are PUT requests. Out of 20 messages that form the GET requests, 10 are
# confirmable messages (CON) and 10 are non-confirmable messages (NON). It is
# the same for 20 messages that form the PUT requests. The number of CON and
# NON messages can be configured with two variables `n_con_msgs` and
# `n_non_msgs`, respectively. The results obtained from this program are stored
# in a new directory called `coap-point-to-point-3(date-timestamp)_dump`. It
# contains a `README` which provides details about the sub-directories and
# files within this directory.

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

# Configure the user options for the application that sends GET requests.
#
# Note: the `coap_non_timeout` parameter configured below is required for NON
# messages only. In CoAP, NON messages are not acknowledged by the receiving
# host, but if there is a `request` inside a NON message, the receiving host
# sends a `response`. However, if the NON message gets dropped in the network,
# the sender would never get a response. The `coap_non_timeout` parameter is
# required in such cases.
#
# Setting a low value for `coap_non_timeout` parameter is not recommended
# because the timeout might expire while the response is on its way to the
# sender. The unit of `coap_non_timeout` parameters is seconds.
user_options_application_1 = {
    "coap_request_type": "get",  # Set the request type to GET
    "coap_server_content": "This is the payload when server responds to a GET request",
    "coap_non_timeout": "5.0",  # Timeout associated with requests sent via NON
}

# Configure the user options for the application that sends PUT requests.
user_options_application_2 = {
    "coap_request_type": "put",  # Set the request type to PUT
    "coap_message_payload": "This is the payload when client sends the PUT request",
    "coap_non_timeout": "5.0",  # Timeout associated with requests sent via NON
}

# Set the number of CON and NON messages to 10 each.
n_con_msgs = 10
n_non_msgs = 10

# Configure two applications from `h1` to `h2`. `application1` sends 20 GET requests (10 CON,
# 10 NON) and `application2` sends 20 PUT requests (10 CON, 10 NON).
application1 = CoapApplication(
    h1, h2, eth2.get_address(), n_con_msgs, n_non_msgs, user_options_application_1
)

application2 = CoapApplication(
    h1, h2, eth2.get_address(), n_con_msgs, n_non_msgs, user_options_application_2
)

# Use both the applications as `CoAP` applications.
exp.add_coap_application(application1)
exp.add_coap_application(application2)

# Run the experiment
exp.run()
