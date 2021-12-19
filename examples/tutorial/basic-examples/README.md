# Basic examples to get started with NeST

This directory contains the following examples to get started with `NeST`,
and we recommend that the beginners walk through these examples in the same
order as they are presented:

## 1. point-to-point-1.py
This program emulates a point to point network between two hosts `h1` and
`h2`. One ping packet is sent from `h1` to `h2`, and the success/failure
of ping is reported. The main aim of this example is to demonstrate the usage
of basic APIs of NeST to create a network topology, configure link attributes,
assign IPv4 addresses and test the connectivity between two hosts.

## 2. point-to-point-2.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via a router `r1`. One ping packet is sent from `h1` to `h2`, and
the success/failure of ping is reported. This example extends the
`point-to-point-1.py` example. The main aim of this example is to demonstrate
how two networks can be interconnected by using a router. The steps to enable
IPv4 forwarding in the router and setting default routes in the hosts are
covered in this program. We manually set the routes because we are not using
dynamic routing protocols like RIP, OSPF and others.

## 3. point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via two routers `r1` and `r2`. One ping packet is sent from `h1`
to `h2`, and the success/failure of ping is reported. This example extends the
`point-to-point-2.py` example. The main aim of this example is to demonstrate
how two networks can be interconnected by a network of routers. Besides
enabling IPv4 forwarding and setting default routes in hosts, this example
requires setting default routes in the routers.

## 4. simple-lan.py
This program emulates a Local Area Network (LAN). Four hosts: `h1` to `h4`
are connected using a switch `s1`. One ping packet is sent from `h1` to `h2`
and another from `h3` to `h4`. The success/failure of ping is reported. This
example demonstrates how to use the `Switch` class in NeST to set up a LAN.

## 5. two-lans-connected-directly.py
This program emulates two Local Area Networks (LANs) connected directly to
each other. LAN-1 consists of three hosts `h1` to `h3` connected to switch
`s1`, and LAN-2 consists three hosts `h4` to `h6` connected to switch `s2`.
Switches `s1` and `s2` are connected to each other. One ping packet is sent
from `h1` to `h4`, another from `h2` to `h5` and lastly, from `h3` to `h6`.
The success/failure of ping is reported. This program extends `simple-lan.py`.
