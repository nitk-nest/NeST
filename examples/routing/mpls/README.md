# Examples to understand the support of MPLS in NeST

This directory contains the examples to demonstrate how Multi Protocol Label
Switching (MPLS) can be used in `NeST`.

`IMPORTANT`
Note 1: MPLS modules are not enabled by default in Linux. Hence, before
running these programs, enable the MPLS modules as explained below (ignore if
MPLS modules are already enabled):

```shell
modprobe mpls_iptunnel
modprobe mpls_router
modprobe mpls_gso
```

Verify whether the MPLS modules are loaded:

```shell
`lsmod | grep mpls`
```

Note 2: The third example listed below, which demonstrates the usage of Label
Distribution Protocol (LDP), requires Free Range Routing (FRR) suite to be
pre-installed. See the README in `examples/routing/frr` to install FRR. It is
highly recommended that, after installing FRR, at least one of the examples
provided in `examples/routing/frr` is run to confirm that FRR is successfully
installed.

## 1. mpls-basic-ce-pe-routers.py
This program demonstrates how to set up a MPLS network that connects two
customer edge (ce) routers `ce1` and `ce2` via two provider edge (pe) routers
`pe1` and `pe2`. All routers are MPLS enabled. The labels are assigned
manually and Penultimate Hop Popping (PHP) is used in this program. Address
helper is used to assign the IPv4 addresses to the interfaces. Five ping
packets are sent from `ce1` to `ce2`, and the success/failure of these packets
is reported.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: mpls-basic-ce-pe-routers.py -->

## 2. mpls-ce-pe-p-routers.py
This program demonstrates how to set up a MPLS network that connects two
customer edge (ce) routers `ce1` and `ce2` via two provider edge (pe) routers
`pe1` and `pe2`, which are further connected via a provider (p) router. Only
`pe` and `p` routers are MPLS enabled. `ce` routers do not use MPLS. The
labels are assigned manually and Penultimate Hop Popping (PHP) is used in
this program. Address helper is used to assign the IPv4 addresses to the
interfaces. Five ping packets are sent from `ce1` to `ce2`, and the
success/failure of these packets is reported.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: mpls-ce-pe-p-routers.py -->

## 3. mpls-ldp-ce-pe-p-routers.py
This program demonstrates how to set up a MPLS network that connects two
customer edge (ce) routers `ce1` and `ce2` via two provider edge (pe) routers
`pe1` and `pe2`, which are further connected via a provider (p) router. Only
`pe` and `p` routers are MPLS enabled. `ce` routers do not use MPLS. The
labels are assigned automatically using the Label Distribution Protocol (LDP).
This program uses LDP from Free Range Routing (FRR) suite. LDP requires an IP
based dynamic routing protocol to be already in place for it to find out the
IP addresses. In this program, we use Open Shortest Path First (OSPF) routing
protocol. Penultimate Hop Popping (PHP) is used in this program. Address helper
is used to assign the IPv4 addresses to the interfaces. Five ping packets are
sent from `ce1` to `ce2`, and the success/failure of these packets is reported.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: mpls-ldp-ce-pe-p-routers.py -->

## 4. mpls-ldp-ce-pe-p-routers-multi-address.py
This program demonstrates how to set up a MPLS network that connects two
customer edge (ce) routers `ce1` and `ce2` via two provider edge (pe) routers
`pe1` and `pe2`, which are further connected via a provider (p) router. But
here both IPv4 and IPv6 addresses are assigned to the interfaces. Only `pe` and
`p` routers are MPLS enabled. `ce` routers do not use MPLS. The labels are
assigned automatically using the Label Distribution Protocol (LDP). This
program uses LDP from Free Range Routing (FRR) suite. Penultimate Hop Popping
(PHP) is used in this program. Address helper is used to assign the IPv6
addresses to the interfaces, IPv4 addresses are added manually. Five ping
packets are sent from `ce1` to `ce2`, and the success/failure of these packets
is reported.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: mpls-ldp-ce-pe-p-routers-multi-address.py -->

Once these programs are understood, and if MPLS modules are no longer needed,
they can be disabled using:

```shell
rmmod mpls_iptunnel
rmmod mpls_router
rmmod mpls_gso
```
