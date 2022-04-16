# Examples to demonstrate how to generate UDP traffic in NeST

This directory contains the following examples to understand how UDP traffic
can be generated in `NeST`. `Flow` API is used in these examples to configure
flows between a pair of hosts. We recommend that you walk through these
examples in the same order as they are presented.

## 1. udp-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via two routers `r1` and `r2`. It is similar to the
`ah-point-to-point-3.py` example in `examples/address-helpers`. Instead
of `ping`, one UDP flow is configured from `h1` to `h2`. The links between
`h1` to `r1` and between `r2` to `h2` are edge links. The link between `r1`
and `r2` is the bottleneck link with lesser bandwidth and higher propagation
delays. Address helper is used in this program to assign IPv4 addresses.

This program runs for 50 seconds and creates a new directory called
`udp-point-to-point-3(date-timestamp)_dump`. It contains a `README` which
provides details about the sub-directories and files within this directory.
For this program, see the plots in `iperf3` and `ping` sub-directories.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: udp-point-to-point-3.py -->

## 2. udp-simple-lan.py
This program emulates a Local Area Network (LAN). Four hosts: `h1` to `h4`
are connected using a switch `s1`. It is similar to the `ah-simple-lan.py`
example in `examples/address-helpers`. Instead of `ping`, one UDP
flow is configured from `h1` to `h2` and another from `h3` to `h4`.
Address helper is used in this program to assign IPv4 addresses.

This program runs for 50 seconds and creates a new directory called
`udp-simple-lan(date-timestamp)_dump`. It contains a `README` which
provides details about the sub-directories and files within this directory.
For this program, see the plots in `iperf3` and `ping` sub-directories.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: udp-simple-lan.py -->
