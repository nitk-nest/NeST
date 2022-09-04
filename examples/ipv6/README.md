# Examples to understand the support of IPv6 addressing in NeST

This directory contains the following examples to understand how IPv6 addresses
can be used in `NeST`. We recommend that you walk through these examples in
the same order as they are presented.

**NOTE**  
Duplicate Address Detection (DAD) feature of IPv6 in Linux is disabled by
default in NeST. It can be enabled by using the `config` as shown [here](http://nest.nitk.ac.in/docs/master/user/config.html).
However, you might have to manually add delays during the IPv6 address
assignment in NeST if you enable the DAD feature. Hence, enabling the DAD
feature in NeST is recommended only for those users who are familiar about
the functionality of DAD and can tweak the network experiment as required.

## 1. ipv6-point-to-point-1.py
This program emulates a point to point network between two hosts `h1` and
`h2`. Five ping packets are sent from `h1` to `h2`, and the success/failure
of these packets is reported. It is similar to `point-to-point-1.py` available
in `examples/basic-examples`, the only difference is that IPv6 addresses are
used in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ipv6-point-to-point-1.py -->

## 2. ipv6-point-to-point-2.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via a router `r1`. Five ping packets are sent from `h1` to `h2`, and
the success/failure of these packets is reported. This example extends the
`ipv6-point-to-point-1.py` example. It is similar to `point-to-point-2.py`
available in `examples/basic-examples`, the only difference is that IPv6
addresses are used in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ipv6-point-to-point-2.py -->

## 3. ipv6-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via two routers `r1` and `r2`. Five ping packets are sent from `h1`
to `h2`, and the success/failure of these packets is reported. This example
extends the `ipv6-point-to-point-2.py` example. It is similar to
`point-to-point-3.py` available in `examples/basic-examples`, the only
difference is that IPv6 addresses are used in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ipv6-point-to-point-3.py -->

## 4. ipv6-simple-lan.py
This program emulates a Local Area Network (LAN). Four hosts: `h1` to `h4`
are connected using a switch `s1`. Five ping packets are sent from `h1` to `h2`
and five ping packets from `h3` to `h4`. The success/failure of these packets
is reported. It is similar to `simple-lan.py` available in
`examples/basic-examples`, the only difference is that IPv6 addresses are used
in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ipv6-simple-lan.py -->

## 5. ipv6-two-lans-connected-directly.py
This program emulates two Local Area Networks (LANs) connected directly to
each other. LAN-1 consists of three hosts `h1` to `h3` connected to switch
`s1`, and LAN-2 consists three hosts `h4` to `h6` connected to switch `s2`.
Switches `s1` and `s2` are connected to each other. Five ping packets are sent
from `h1` to `h4`, five from `h2` to `h5`, and lastly, five from `h3` to `h6`.
The success/failure of these packets is reported. This program extends
`ipv6-simple-lan.py`. It is similar to `two-lans-connected-directly.py`
available in `examples/basic-examples`, the only difference is that IPv6
addresses are used in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ipv6-two-lans-connected-directly.py -->

## 6. ipv6-two-lans-connected-via-router.py
This program emulates two Local Area Networks (LANs) connected via a router.
LAN-1 consists three hosts `h1` to `h3` connected to switch `s1`, and
LAN-2 consists three hosts `h4` to `h6` connected to switch `s2`. Switches
`s1` and `s2` are connected to each other via a router `r1`. Five ping
packets are sent from `h1` to `h4`, five from `h2` to `h5` and lastly, five
from `h3` to `h6`. The success/failure of these packets is reported. It is
similar to `two-lans-connected-via-router.py` available in
`examples/basic-examples`, the only difference is that IPv6 addresses are
used in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ipv6-two-lans-connected-via-router.py -->

## 7. ipv6-v4-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via two routers `r1` and `r2`. It is similar to
`ipv6-point-to-point-3.py` available in `examples/ipv6`, the only difference
is that both IPv4 and IPv6 addresses are assigned to hosts and routers. Five
ping packets are sent from `h1` to `h2`, first with IPv4 addresses and then
with IPv6 addresses. The success/failure of these packets is reported.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: ipv6-v4-point-to-point-3.py -->
