# Examples to demonstrate the usage of Address Helpers in NeST

This directory contains the following examples to understand how address
helpers can be used in `NeST` to automatically assign IPv4/IPv6 addresses.
These helpers can avoid the overhead of manually assigning the addresses.
We recommend that you walk through these examples in the same order as they
are presented.

## 1. ah-point-to-point-1.py
This program emulates a point to point network between two hosts `h1` and
`h2`. Five ping packets are sent from `h1` to `h2`, and the success/failure
of these packets is reported. This program is similar to `point-to-point-1.py`
available in `examples/basic-examples`, the only difference is that we use an
address helper in this program to assign IPv4 addresses to interfaces instead
of manually assigning them. Note that two packages: `Network` and
`AddressHelper` are imported in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ah-point-to-point-1.py -->

## 2. ah-point-to-point-2.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via a router `r1`. Five ping packets are sent from `h1` to `h2`, and
the success/failure of these packets is reported. This program is similar to
`point-to-point-2.py` available in `examples/basic-examples`, the only
difference is that we use an address helper in this program to assign IPv4
addresses to interfaces instead of manually assigning them. Note that two
packages: `Network` and `AddressHelper` are imported in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ah-point-to-point-2.py -->

## 3. ah-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. Five ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`point-to-point-3.py` available in `examples/basic-examples`, the only
difference is that we use an address helper in this program to assign IPv4
addresses to interfaces instead of manually assigning them. Note that two
packages: `Network` and `AddressHelper` are imported in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ah-point-to-point-3.py -->

## 4. ah-simple-lan.py
This program emulates a Local Area Network (LAN). Four hosts: `h1` to `h4`
are connected using a switch `s1`. Five ping packets are sent from `h1` to
`h2`, and five ping packets from `h3` to `h4`. The success/failure of these
packets is reported. It is similar to `simple-lan.py` available in
`examples/basic-examples`, the only difference is that we use an address
helper in this program to assign IPv4 addresses to interfaces instead of
manually assigning them. Note that two packages: `Network` and
`AddressHelper` are imported in this program. Since all the interfaces in this
example belong to the same network, we demonstrate a simpler approach to use
the `Network` API.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ah-simple-lan.py -->

## 5. ah-two-lans-connected-directly.py
This program emulates two Local Area Networks (LANs) connected directly to
each other. LAN-1 consists three hosts `h1` to `h3` connected to switch `s1`,
and LAN-2 consists three hosts `h4` to `h6` connected to switch `s2`.
Switches `s1` and `s2` are connected to each other. Five ping packets are sent
from `h1` to `h4`, five from `h2` to `h5`, and lastly, five from `h3` to `h6`.
The success/failure of these packets is reported. It is similar to
`two-lans-directly-connected.py` available in `examples/basic-examples`, the
only difference is that we use an address helper in this program to assign IPv4
addresses to interfaces instead of manually assigning them. Note that two
packages: `Network` and `AddressHelper` are imported in this program. Since all
the interfaces in this example belong to the same network, we demonstrate a
simpler approach to use the `Network` API.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ah-two-lans-connected-directly.py -->

## 6. ah-two-lans-connected-via-router.py
This program emulates two Local Area Networks (LANs) connected via a router.
LAN-1 consists three hosts `h1` to `h3` connected to switch `s1`, and LAN-2
consists three hosts `h4` to `h6` connected to switch `s2`. Switches `s1`
and `s2` are connected to each other via a router `r1`. Five ping packets are
sent from `h1` to `h4`, five from `h2` to `h5` and lastly, five from `h3` to
`h6`. The success/failure of these packets is reported. It is similar to
`two-lans-connected-via-router.py` available in `examples/basic-examples`,
the only difference is that we use an address helper in this program to
assign IPv4 addresses to interfaces instead of manually assigning them. Note
that two packages: `Network` and `AddressHelper` are imported in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ah-two-lans-connected-via-router.py -->

## 7. ipv6-ah-point-to-point-1.py
This program emulates a point to point network between two hosts `h1` and
`h2`. Five ping packets are sent from `h1` to `h2`, and the success/failure
of these packets is reported. It is similar to `ipv6-point-to-point-1.py`
available in `examples/ipv6`, the only difference is that we use an address
helper in this program to assign IPv6 addresses to interfaces instead of
manually assigning them. Note that two packages: `Network` and `AddressHelper`
are imported in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ipv6-ah-point-to-point-1.py -->

## 8. ipv6-ah-point-to-point-2.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via a router `r1`. Five ping packets are sent from `h1` to `h2`, and
the success/failure of these packets is reported. This program is similar to
`ipv6-point-to-point-2.py` available in `examples/ipv6`, the only difference is
that we use an address helper in this program to assign IPv6 addresses to
interfaces instead of manually assigning them. Note that two packages:
`Network` and `AddressHelper` are imported in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ipv6-ah-point-to-point-2.py -->

## 9. ipv6-ah-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. Five ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ipv6-point-to-point-3.py` available in `examples/ipv6`, the only difference is
that we use an address helper in this program to assign IPv6 addresses to
interfaces instead of manually assigning them. Note that two packages:
`Network` and `AddressHelper` are imported in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ipv6-ah-point-to-point-3.py -->

## 10. ipv6-ah-simple-lan.py
This program emulates a Local Area Network (LAN). Four hosts: `h1` to `h4`
are connected using a switch `s1`. Five ping packets are sent from `h1` to
`h2`, and five ping packets from `h3` to `h4`. The success/failure of these
packets is reported. It is similar to `ipv6-simple-lan.py` available in
`examples/ipv6`, the only difference is that we use an address helper in this
program to assign IPv6 addresses to interfaces instead of manually assigning
them. Note that two packages: `Network` and `AddressHelper` are imported in
this program. Since all the interfaces in this example belong to the same
network, we demonstrate a simpler approach to use the `Network` API.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ipv6-ah-simple-lan.py -->

## 11. ipv6-ah-two-lans-connected-directly.py
This program emulates two Local Area Networks (LANs) connected directly to
each other. LAN-1 consists three hosts `h1` to `h3` connected to switch `s1`,
and LAN-2 consists three hosts `h4` to `h6` connected to switch `s2`.
Switches `s1` and `s2` are connected to each other. Five ping packets are sent
from `h1` to `h4`, five from `h2` to `h5`, and lastly, five from `h3` to `h6`.
The success/failure of these packets is reported. It is similar to
`ipv6-two-lans-connected-directly.py` available in `examples/ipv6`, the only
difference is that we use an address helper in this program to assign IPv6
addresses to interfaces instead of manually assigning them. Note that two
packages: `Network` and `AddressHelper` are imported in this program. Since
all the interfaces in this example belong to the same network, we demonstrate
a simpler approach to use the `Network` API.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ipv6-ah-two-lans-connected-directly.py -->
