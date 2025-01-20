# Examples to demonstrate how to generate HTTP traffic in NeST

This directory contains the following example to understand how Hyper Text
Transfer Protocol (HTTP) traffic can be generated in `NeST`.
`HttpApplication` API is used in these examples to configure flows between a
pair of hosts.

## 1. HTTP-point-to-point-3.py
This program emulates a Local Area Network (LAN). Four hosts: `h1` to `h4`
are connected using a switch `s1`. Here, `h4` is taken as the HTTP Server and
`H1`, `H2`, `H3` act as HTTP Clients. They generate load for the H$ server with
varying number of connections and rate. The results of this HTTP experiment
will be documented in the `examples/<Exp Name>(<Timestamp>)_dump` folder. It  contains a `README` which
provides details about the sub-directories and files within this directory.
