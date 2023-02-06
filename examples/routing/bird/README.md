# Examples to show the use of BIRD Internet Routing Daemon (BIRD) Suite in NeST

This directory contains the examples to demonstrate how BIRD Internet Routing
Daemon (BIRD) suite can be used for emulating dynamic routing in `NeST`.

`IMPORTANT`: BIRD module is not installed by default in Linux. Hence, before
running this program, install the BIRD module as explained below (ignore if
BIRD is already installed).

BIRD can be obtained from your Linux distribution packages. For Ubuntu, run:

```shell
sudo apt install bird
```

## 1. bird-ospf-point-to-point-2.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via a router `r1`. Five ping packets are sent from `h1` to `h2`, and
the success/failure of these packets is reported. It is similar to
`ah-point-to-point-2.py` available in `examples/address-helpers`, the only
difference is that we use Open Shortest Path First (OSPF), a dynamic routing
protocol, instead of manually configuring the routes. This program uses OSPF
from BIRD Internet Routing Daemon (BIRD) suite for dynamic routing. A new
package called `RoutingHelper` is imported in this program. The routing
logs are written to files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: bird-ospf-point-to-point-2.py -->

## 2. bird-ospf-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. Five ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` available in `examples/address-helpers`, the only
difference is that we use Open Shortest Path First (OSPF), a dynamic routing
protocol, instead of manually configuring the routes. This program uses OSPF
from BIRD Internet Routing Daemon (BIRD) suite for dynamic routing. A new
package called `RoutingHelper` is imported in this program. The routing logs
are written to files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: bird-ospf-point-to-point-3.py -->

## 3. bird-rip-point-to-point-2.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via a router `r1`. Five ping packets are sent from `h1` to `h2`, and
the success/failure of these packets is reported. It is similar to
`ah-point-to-point-2.py` available in `examples/address-helpers`, the only
difference is that we use Routing Information Protocol (RIP), a dynamic routing
protocol, instead of manually configuring the routes. This program uses RIP
from BIRD Internet Routing Daemon (BIRD) suite for dynamic routing. A new
package called `RoutingHelper` is imported in this program. The routing logs
are written to files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: bird-rip-point-to-point-2.py -->

## 4. bird-rip-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. Five ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` available in `examples/address-helpers`, the only
difference is that we use Routing Information Protocol (RIP), a dynamic
routing protocol, instead of manually configuring the routes. This program
uses RIP from BIRD Internet Routing Daemon (BIRD) suite for dynamic routing.
A new package called `RoutingHelper` is imported in this program. The routing
logs are written to files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: bird-rip-point-to-point-3.py -->

`Note`: The above examples can be modified to work with IPv6 addressing by
changing the IPv4 subnets to IPv6 subnets. Replace IPv4 subnets
`192.168.1.0/24`, `192.168.2.0/24` and `192.168.13.0/24` by IPv6 subnets
`2001:1::/122`, `2001:2::/122` and `2001:3::/122`, respectively.
