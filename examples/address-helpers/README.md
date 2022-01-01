# Examples to understand the support of IPv6 addressing in NeST

This directory contains the following examples to understand how address
helpers can be used in `NeST` to automatically assign IPv4/IPv6 addresses.
These helpers can avoid the overhead of manually assigning the addresses.
We recommend that you walk through these examples in the same order as they
are presented.

## 1. ah-point-to-point-1.py
This program emulates a point to point network between two hosts `h1` and
`h2`. One ping packet is sent from `h1` to `h2`, and the success/failure
of ping is reported. This program is similar to the `point-to-point-1.py`
example available in `examples/tutorial/basic-examples`, the only difference
is that we use an address helper in this program to assign IPv4 addresses to
interfaces instead of manually assigning them. Note that two packages:
`Network` and `AddressHelper` are imported in this program.

## 2. ah-point-to-point-2.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via a router `r1`. One ping packet is sent from `h1` to `h2`, and
the success/failure of ping is reported. This program is similar to the
`point-to-point-2.py` example available in `examples/tutorial/basic-examples`,
the only difference is that we use an address helper in this program to
assign IPv4 addresses to interfaces instead of manually assigning them. Note
that two packages: `Network` and `AddressHelper` are imported in this program.

## 3. ah-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. One ping packet is sent from `h1` to `h2`
and the success/failure of ping is reported. This program is similar to the
`point-to-point-3.py` example available in `examples/tutorial/basic-examples`,
the only difference is that we use an address helper in this program to
assign IPv4 addresses to interfaces instead of manually assigning them. Note
that two packages: `Network` and `AddressHelper` are imported in this program.

## 4. ipv6-ah-point-to-point-1.py
This program emulates a point to point network between two hosts `h1` and
`h2`. One ping packet is sent from `h1` to `h2`, and the success/failure
of ping is reported. This program is similar to the `ipv6-point-to-point-1.py`
example available in `examples/ipv6`, the only difference is that we use an
address helper in this program to assign IPv6 addresses to interfaces instead
of manually assigning them. Note that two packages: `Network` and
`AddressHelper` are imported in this program.

## 5. ipv6-ah-point-to-point-2.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via a router `r1`. One ping packet is sent from `h1` to `h2`, and
the success/failure of ping is reported. This program is similar to the
`ipv6-point-to-point-2.py` example available in `examples/ipv6`, the only
difference is that we use an address helper in this program to assign IPv6
addresses to interfaces instead of manually assigning them. Note that two
packages: `Network` and `AddressHelper` are imported in this program.

## 6. ipv6-ah-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. One ping packet is sent from `h1` to `h2`
and the success/failure of ping is reported. This program is similar to the
`ipv6-point-to-point-3.py` example available in `examples/ipv6`, the only
difference is that we use an address helper in this program to assign IPv6
addresses to interfaces instead of manually assigning them. Note that two
packages: `Network` and `AddressHelper` are imported in this program.
