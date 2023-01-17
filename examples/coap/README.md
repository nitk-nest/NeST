# Examples to demonstrate how to generate CoAP traffic in NeST

This directory contains the following example to understand how Contrained
Application Protocol (CoAP) traffic can be generated in `NeST`. `CoapApplication` API
is used in these examples to configure flows between a pair of hosts.

## 1. coap-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via two routers `r1` and `r2`. It is similar to the
`udp-point-to-point-3.py` example in `examples/udp`. Instead of a UDP flow,
two CoAP flows are configured from `h1` to `h2`, one for sending the GET
requests and another for sending the PUT requests. `h1` acts as a CoAP client
and `h2` acts as a CoAP server. Address helper is used in this program to
assign IPv4 addresses.

This program sends a total of 40 CoAP messages: 20 are GET requests and 20 are
PUT requests. Out of 20 messages that form the GET requests, 10 are confirmable
messages (CON) and 10 are non-confirmable messages (NON). It is the same for 20
messages that form the PUT requests. The number of CON and NON messages can be
configured with two variables `n_con_msgs` and `n_non_msgs`, respectively. The
results obtained from this program are stored in a new directory called
`coap-point-to-point-3(date-timestamp)_dump`. It  contains a `README` which
provides details about the sub-directories and files within this directory.
