# Examples to demonstrate how to configure queue disciplines (qdiscs) using NeST

This directory contains the following examples to understand how queue
disciplines can be configured using `NeST`.

## 1. choke-point-to-point.py
This program emulates point to point networks that connect four hosts: `h1`
- `h4` via two routers `r1` and `r2`. One TCP flow is configured from `h1` to
`h3` and one UDP flow is configured from `h2` to `h4`. It is similar to
`tcp-udp-point-to-point.py` in `examples/tcp`. The links `h1` <--> `r1`,
`h2` <--> `r1`, and `r2` <--> `h3`, `r2` <--> `h4` are edge links. The link
`r1` <--> `r2` is the bottleneck link with lesser bandwidth and higher
propagation delays. This program demonstrates how to configure CHOose and
Keep for responsive flows, CHOose and Kill for unresponsive flows (`choke`)
queue discipline (qdisc) and obtain the relevant statistics. `choke` is
enabled on the link from `r1` to `r2`, but not from `r2` to `r1` because
data packets flow in one direction only (left to right) in this example.

This program runs for 200 seconds and creates a new directory called
`choke-point-to-point(date-timestamp)_dump`. It contains a `README` that
provides details about the sub-directories and files within this directory.
See the plots in `netperf`, `ping` and `ss` sub-directories for this program.

NOTE: This program does not generate the stats for `choke` qdisc because NeST
does not support this feature yet.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: choke-point-to-point.py -->

## 2. codel-point-to-point.py
This program emulates point to point networks that connect four hosts: `h1`
- `h4` via two routers `r1` and `r2`. One TCP flow is configured from `h1` to
`h3` and one UDP flow is configured from `h2` to `h4`. It is similar to
`tcp-udp-point-to-point.py` in `examples/tcp`. The links `h1` <--> `r1`,
`h2` <--> `r1`, and `r2` <--> `h3`, `r2` <--> `h4` are edge links. The link
`r1` <--> `r2` is the bottleneck link with lesser bandwidth and higher
propagation delays. This program demonstrates how to configure Controlled
Delay (`codel`) queue discipline (qdisc) and obtain the relevant statistics.
`codel` is enabled on the link from `r1` to `r2`, but not from `r2` to `r1`
because data packets flow in one direction only (left to right) in this
example.

This program runs for 200 seconds and creates a new directory called
`codel-point-to-point(date-timestamp)_dump`. It contains a `README` that
provides details about the sub-directories and files within this directory.
See the plots in `netperf`, `ping`, `ss` and `tc` sub-directories for this
program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: codel-point-to-point.py -->

## 3. fq-codel-point-to-point.py
This program emulates point to point networks that connect four hosts: `h1`
- `h4` via two routers `r1` and `r2`. One TCP flow is configured from `h1` to
`h3` and one UDP flow is configured from `h2` to `h4`. It is similar to
`tcp-udp-point-to-point.py` in `examples/tcp`. The links `h1` <--> `r1`,
`h2` <--> `r1`, and `r2` <--> `h3`, `r2` <--> `h4` are edge links. The link
`r1` <--> `r2` is the bottleneck link with lesser bandwidth and higher
propagation delays. This program demonstrates how to configure Flow Queue
Controlled Delay (`fq_codel`) queue discipline (qdisc) and obtain relevant
statistics. `fq_codel` is enabled on the link from `r1` to `r2`, but not from
`r2` to `r1` because data packets flow in one direction only (left to right)
in this example.

This program runs for 200 seconds and creates a new directory called
`fq-codel-point-to-point(date-timestamp)_dump`. It contains a `README` that
provides details about the sub-directories and files within this directory.
See the plots in `netperf`, `ping`, `ss` and `tc` sub-directories for this
program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: fq-codel-point-to-point.py -->

## 4. fq-pie-point-to-point.py
This program emulates point to point networks that connect four hosts: `h1`
- `h4` via two routers `r1` and `r2`. One TCP flow is configured from `h1` to
`h3` and one UDP flow is configured from `h2` to `h4`. It is similar to
`tcp-udp-point-to-point.py` in `examples/tcp`. The links `h1` <--> `r1`,
`h2` <--> `r1`, and `r2` <--> `h3`, `r2` <--> `h4` are edge links. The link
`r1` <--> `r2` is the bottleneck link with lesser bandwidth and higher
propagation delays. This program demonstrates how to configure Flow Queue
Proportional Integral controller Enhanced (`fq_pie`) queue discipline (qdisc)
and obtain the relevant statistics. `fq_pie` is enabled on the link from `r1`
to `r2`, but not from `r2` to `r1` because data packets flow in one direction
only (left to right) in this example.

This program runs for 200 seconds and creates a new directory called
`fq-pie-point-to-point(date-timestamp)_dump`. It contains a `README` that
provides details about the sub-directories and files within this directory.
See the plots in `netperf`, `ping`, `ss` and `tc` sub-directories for this
program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: fq-pie-point-to-point.py -->

## 5. pfifo-point-to-point.py
This program emulates point to point networks that connect four hosts: `h1`
- `h4` via two routers `r1` and `r2`. One TCP flow is configured from `h1` to
`h3` and one UDP flow is configured from `h2` to `h4`. It is similar to
`tcp-udp-point-to-point.py` in `examples/tcp`. The links `h1` <--> `r1`,
`h2` <--> `r1`, and `r2` <--> `h3`, `r2` <--> `h4` are edge links. The link
`r1` <--> `r2` is the bottleneck link with lesser bandwidth and higher
propagation delays. This program demonstrates how to configure `pfifo` queue
discipline (qdisc) and obtain the relevant statistics. `pfifo` is enabled on
the link from `r1` to `r2`, but not from `r2` to `r1` because data packets
flow in one direction only (left to right) in this example.

This program runs for 200 seconds and creates a new directory called
`pfifo-point-to-point(date-timestamp)_dump`. It contains a `README` that
provides details about the sub-directories and files within this directory.
See the plots in `netperf`, `ping`, `ss` and `tc` sub-directories for this
program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: pfifo-point-to-point.py -->

## 6. pie-point-to-point.py
This program emulates point to point networks that connect four hosts: `h1`
- `h4` via two routers `r1` and `r2`. One TCP flow is configured from `h1` to
`h3` and one UDP flow is configured from `h2` to `h4`. It is similar to
`tcp-udp-point-to-point.py` in `examples/tcp`. The links `h1` <--> `r1`,
`h2` <--> `r1`, and `r2` <--> `h3`, `r2` <--> `h4` are edge links. The link
`r1` <--> `r2` is the bottleneck link with lesser bandwidth and higher
propagation delays. This program demonstrates how to configure Proportional
Integral controller Enhanced (`pie`) queue discipline (qdisc) and obtain the
relevant statistics. `pie` is enabled on the link from `r1` to `r2`, but
not from `r2` to `r1` because data packets flow in one direction only (left
to right) in this example.

This program runs for 200 seconds and creates a new directory called
`pie-point-to-point(date-timestamp)_dump`. It contains a `README` that
provides details about the sub-directories and files within this directory.
See the plots in `netperf`, `ping`, `ss` and `tc` sub-directories for this
program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: pie-point-to-point.py -->

## 7. red-point-to-point.py
This program emulates point to point networks that connect four hosts: `h1`
- `h4` via two routers `r1` and `r2`. One TCP flow is configured from `h1` to
`h3` and one UDP flow is configured from `h2` to `h4`. It is similar to
`tcp-udp-point-to-point.py` in `examples/tcp`. The links `h1` <--> `r1`,
`h2` <--> `r1`, and `r2` <--> `h3`, `r2` <--> `h4` are edge links. The link
`r1` <--> `r2` is the bottleneck link with lesser bandwidth and higher
propagation delays. This program demonstrates how to configure Random Early
Detection (`red`) queue discipline (qdisc) and obtain relevant statistics.
`red` is enabled on the link from `r1` to `r2`, but not from `r2` to `r1`
because data packets flow in one direction only (left to right) in this
example.

This program runs for 200 seconds and creates a new directory called
`red-point-to-point(date-timestamp)_dump`. It contains a `README` that
provides details about the sub-directories and files within this directory.
See the plots in `netperf`, `ping` and `ss` sub-directories for this program.

NOTE: This program does not generate the stats for `red` qdisc because NeST
does not support this feature yet.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: red-point-to-point.py -->
