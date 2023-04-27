# Examples to demonstrate how to generate TCP traffic in NeST

This directory contains the following examples to understand how TCP traffic
can be generated in `NeST`. `Flow` API is used in these examples to configure
flows between a pair of hosts.

`IMPORTANT`
Note 1: The third example listed below, which demonstrates how to disable
offloads in NeST, requires `ethtool` to be pre-installed in your machine.
It can be installed on debian based systems as:

```shell
sudo apt install ethtool
```

## 1. dctcp-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via two switches `s1` and `s2`. This program is similar to
`udp-point-to-point-3.py` in `examples/udp`. One DCTCP flow
is configured from `h1` to `h2`. The links between `h1` to `s1` and between
`s2` to `h2` are edge links. The link between `s1` and `s2` is the bottleneck
link with lesser bandwidth and higher propagation delays. `codel` queue
discipline is enabled on the link from `s1` to `s2`, but not from `s2` to
`s1` because data packets flow in one direction only (`h1` to `h2`) in this
example.

This program runs for 200 seconds and creates a new directory called
`dctcp-point-to-point-3(date-timestamp)_dump`. It contains a `README` which
provides details about the sub-directories and files within this directory.
See the plots in `netperf`, `ping` and `ss` sub-directories for this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: dctcp-point-to-point-3.py -->

## 2. tcp-bbr-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via two routers `r1` and `r2`. This program is similar to
`udp-point-to-point-3.py` in `examples/udp`. Instead of UDP, one TCP BBR flow
is configured from `h1` to `h2`. The links between `h1` to `r1` and between
`r2` to `h2` are edge links. The link between `r1` and `r2` is the bottleneck
link with lesser bandwidth and higher propagation delays. `pfifo` queue
discipline is enabled on the link from `r1` to `r2`, but not from `r2` to
`r1` because data packets flow in one direction only (`h1` to `h2`) in this
example. Address helper is used in this program to assign IPv4 addresses.

This program runs for 200 seconds and creates a new directory called
`tcp-bbr-point-to-point-3(date-timestamp)_dump`. It contains a `README` which
provides details about the sub-directories and files within this directory.
See the plots in `netperf`, `ping` and `ss` sub-directories for this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: tcp-bbr-point-to-point-3.py -->

## 3. tcp-cubic-parameters-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via two routers `r1` and `r2`. This program is similar to
`tcp-bbr-point-to-point-3.py` in `examples/tcp`. Instead of TCP BBR
algorithm, TCP CUBIC algorithm is used for congestion control. This example
demonstrates how to customize the beta parameter for TCP CUBIC algorithm.

This program runs for 200 seconds and creates two new directories called
`tcp-cubic-parameters-point-to-point-3-default(date-timestamp)_dump`
and `tcp-cubic-parameters-point-to-point-3-beta=1000(date-timestamp)_dump`.
They contain a `README` which provides details about the sub-directories
and files within this directory. See the plots in `netperf`, `ping`
and `ss` sub-directories for this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: tcp-cubic-parameters-point-to-point-3.py -->

## 4. tcp-cubic-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via two routers `r1` and `r2`. This program is similar to
`udp-point-to-point-3.py` in `examples/udp`. Instead of UDP, one TCP CUBIC
flow is configured from `h1` to `h2`. The links between `h1` to `r1` and
between `r2` to `h2` are edge links. The link between `r1` and `r2` is the
bottleneck link with lesser bandwidth and higher propagation delays. `pfifo`
queue discipline is enabled on the link from `r1` to `r2`, but not from `r2`
to `r1` because data packets flow in one direction only (`h1` to `h2`) in
this example. Address helper is used in this program to assign IPv4 addresses.

This program runs for 200 seconds and creates a new directory called
`tcp-cubic-point-to-point-3(date-timestamp)_dump`. It contains a `README`
which provides details about the sub-directories and files within this
directory. See the plots in `netperf`, `ping` and `ss` sub-directories for
this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: tcp-cubic-point-to-point-3.py -->

## 5. tcp-cubic-ssr-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via two routers `r1` and `r2`. This program is similar to
`tcp-cubic-point-to-point-3.py` in `examples/tcp`. This example demonstrates
how to disable and re-enable Slow Start Restart (SSR). By default, SSR is
enabled in Linux kernel.

This program runs for 200 seconds and creates a new directory called
`tcp-cubic-ssr-point-to-point-3(date-timestamp)_dump`. It contains a `README`
which provides details about the sub-directories and files within this
directory. See the plots in `netperf`, `ping` and `ss` sub-directories for
this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: tcp-cubic-ssr-point-to-point-3.py -->

## 6. tcp-cubic-tfo-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via two routers `r1` and `r2`. This program is similar to
`tcp-cubic-point-to-point-3.py` in `examples/tcp`. This example demonstrates
how to disable and re-enable TCP Fast Open (TFO). By default, TFO is
enabled in Linux kernel.

This program runs for 200 seconds and creates a new directory called
`tcp-cubic-tfo-point-to-point-3(date-timestamp)_dump`. It contains a `README`
which provides details about the sub-directories and files within this
directory. See the plots in `netperf`, `ping` and `ss` sub-directories for
this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: tcp-cubic-tfo-point-to-point-3.py -->

## 7. tcp-cubic-wnd-scale-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via two routers `r1` and `r2`. This program is similar to
`tcp-cubic-point-to-point-3.py` in `examples/tcp`. This example demonstrates
how to disable and re-enable Window Scaling in TCP. By default, Window Scaling
is enabled in Linux kernel.

This program runs for 200 seconds and creates a new directory called
`tcp-cubic-wnd-scale-point-to-point-3(date-timestamp)_dump`. It contains
a `README` which provides details about the sub-directories and files within
this directory. See the plots in `netperf`, `ping` and `ss` sub-directories
for this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: tcp-cubic-wnd-scale-point-to-point-3.py -->

## 8. tcp-offloads-point-to-point.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via two routers `r1` and `r2`. This program is similar to
`tcp-cubic-point-to-point-3.py`. It demonstrates how to disable Generic
Segmentation Offload (GSO), Generic Receive Offload (GRO) and TCP
Segmentation Offload (TSO). By default, these offloads are enabled in the
Linux kernel. Address helper is used in this program to assign IPv4 addresses.

This program runs for 200 seconds and creates a new directory called
`tcp-offloads-point-to-point(date-timestamp)_dump`. It contains a `README`
which provides details about the sub-directories and files within this
directory. See the plots in `netperf`, `ping` and `ss` sub-directories for
this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: tcp-offloads-point-to-point.py -->

## 9. tcp-reno-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via two routers `r1` and `r2`. This program is similar to
`udp-point-to-point-3.py` in `examples/udp`. Instead of UDP, one Reno flow
is configured from `h1` to `h2`. The links between `h1` to `r1` and between
`r2` to `h2` are edge links. The link between `r1` and `r2` is the bottleneck
link with lesser bandwidth and higher propagation delays. `pfifo` queue
discipline is enabled on the link from `r1` to `r2`, but not from `r2` to
`r1` because data packets flow in one direction only (`h1` to `h2`) in this
example. Address helper is used in this program to assign IPv4 addresses.

This program runs for 200 seconds and creates a new directory called
`tcp-reno-point-to-point-3(date-timestamp)_dump`. It contains a `README` that
provides details about the sub-directories and files within this directory.
See the plots in `netperf`, `ping` and `ss` sub-directories for this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: tcp-reno-point-to-point-3.py -->

## 10. tcp-udp-point-to-point.py
This program emulates point to point networks that connect four hosts: `h1`
- `h4` via two routers `r1` and `r2`. One TCP flow is configured from `h1` to
`h3` and one UDP flow is configured from `h2` to `h4`.

This program runs for 200 seconds and creates a new directory called
`tcp-udp-point-to-point(date-timestamp)_dump`. It contains a `README` which
provides details about the sub-directories and files within this directory.
See the plots in `iperf3`, `netperf`, `ping` and `ss` sub-directories for
this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: tcp-udp-point-to-point.py -->
