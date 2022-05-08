# Examples to demonstrate the support of static routing in NeST

This directory contains the examples to demonstrate how to use static routing
to populate routing tables for a network in `NeST`.

## 1. static-routing-point-to-point-2.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via a router `r1`. Five ping packets are sent from `h1` to `h2`,
and the success/failure of these packets is reported. This program is
similar to `ah-point-to-point-2.py` available in `examples/address-helpers`,
the only difference is that we populate the routing tables by constructing a
spanning tree of the network using Depth First Search (DFS). A new package
called `RoutingHelper` is imported in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: static-routing-point-to-point-2.py -->

## 2. static-routing-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. Five ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` available in `examples/address-helpers`, the only
difference is that we populate the routing tables by constructing a spanning
tree of the network using Depth First Search (DFS). A new package called
`RoutingHelper` is imported in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: static-routing-point-to-point-3.py -->
