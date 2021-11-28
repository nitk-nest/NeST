# Examples to demonstrate how to generate CoAP traffic in NeST

This directory contains the following examples to understand how CoAP traffic can be generated in `NeST`. `CoapFlow` API is used in these examples to configure flows between a pair of hosts.

## 1. coap-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and `h2` via two routers `r1` and `r2`. It is similar to the `udp-point-to-point-3.py` example in `examples/udp`. Instead of a UDP flow, two CoAP flows are configured from `h1` to `h2`, one for sending GET requests and one for sending PUT requests. The links between `h1` to `r1` and between `r2` to `h2` are edge links. Address helper is used in this program to assign IPv4 addresses.

This program sends 40 CoAP messages through two flows and creates a new directory called `coap-point-to-point-3(date-timestamp)_dump` for storing results. It  contains a `README` which provides details about the sub-directories and files within this directory.

For each flow, the number of NON and CON messages can be configured with two variables `n_con_msgs` and `n_non_msgs`.
