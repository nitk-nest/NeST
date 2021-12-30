# Examples to understand the support of IPv6 addressing in NeST

This directory contains the following examples to understand how IPv6 addresses
can be used in `NeST`. We recommend that you walk through these examples in
the same order as they are presented.

## Note:

Duplicate Address Detection (DAD) feature of IPv6 in Linux is disabled by
default in NeST. It can be enabled by using the `config` as shown [here](http://nest.nitk.ac.in/docs/master/user/config.html).
However, you might have to manually add delays during the IPv6 address
assignment in NeST if you enable the DAD feature. Hence, enabling the DAD
feature in NeST is recommended only for those users who are familiar about
the functionality of DAD and can tweak the network experiment as required.

## 1. ipv6-point-to-point-1.py
This program emulates a point to point network between two hosts `h1` and
`h2`. One ping packet is sent from `h1` to `h2`, and the success/failure
of ping is reported. This program is identical to the `point-to-point-1.py`
example available in `examples/tutorial/basic-examples`, the only difference
is that IPv6 addresses are used in this program.

## 2. ipv6-point-to-point-2.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via a router `r1`. One ping packet is sent from `h1` to `h2`, and
the success/failure of ping is reported. This example extends the
`ipv6-point-to-point-1.py` example. It is identical to the
`point-to-point-2.py` example available in `examples/tutorial/basic-examples`,
the only difference is that IPv6 addresses are used in this program.

## 3. ipv6-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via two routers `r1` and `r2`. One ping packet is sent from `h1`
to `h2`, and the success/failure of ping is reported. This example extends the
`ipv6-point-to-point-2.py` example. It is identical to the
`point-to-point-3.py` example available in `examples/tutorial/basic-examples`,
the only difference is that IPv6 addresses are used in this program.

## 4. ipv6-simple-lan.py
This program emulates a Local Area Network (LAN). Four hosts: `h1` to `h4`
are connected using a switch `s1`. One ping packet is sent from `h1` to `h2`
and another from `h3` to `h4`. The success/failure of ping is reported.This
program is identical to the simple-lan.py example available in
`examples/tutorial/basic-examples`, the only difference is that IPv6 addresses
are used in this program.

## 5. ipv6-two-lans-connected-directly.py
This program emulates two Local Area Networks (LANs) connected directly to
each other. LAN-1 consists of three hosts `h1` to `h3` connected to switch
`s1`, and LAN-2 consists three hosts `h4` to `h6` connected to switch `s2`.
Switches `s1` and `s2` are connected to each other. One ping packet is sent
from `h1` to `h4`, another from `h2` to `h5` and lastly, from `h3` to `h6`.
The success/failure of ping is reported. This program extends
`ipv6-simple-lan.py`. It is identical to the `two-lans-connected-directly.py`
example available in `examples/tutorial/basic-examples`, the only difference
is that IPv6 addresses are used in this program.
