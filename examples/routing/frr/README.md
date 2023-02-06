# Examples to demonstrate the usage of Free Range Routing (FRR) Suite in NeST

This directory contains the examples to demonstrate how Free Range Routing
(FRR) suite can be used for emulating dynamic routing in `NeST`.

`IMPORTANT`: FRR module is not installed by default in Linux. Hence, before
running this program, install the FRR module as explained below (ignore if
FRR is already installed).

FRR can be obtained from your Linux distribution packages. For Ubuntu, run:

(`Credits`: these steps are taken from this link: https://deb.frrouting.org/)

```shell
sudo apt install curl

# Add GPG key
curl -s https://deb.frrouting.org/frr/keys.asc | sudo apt-key add -

# Possible values for FRRVER: frr-6 frr-7 frr-8 frr-stable
# frr-stable will be the latest official stable release
FRRVER="frr-stable"
echo deb https://deb.frrouting.org/frr $(lsb_release -s -c) $FRRVER | sudo tee -a /etc/apt/sources.list.d/frr.list

# Update and install FRR
sudo apt update
sudo apt install frr frr-pythontools
```

Edit `/etc/frr/daemons` with an editor using `sudo` and turn on `ospfd`,
`ospf6d`, `ripd`, `ripngd` and `isisd` (by default they are disabled):

```shell
ospfd=yes
ospf6d=yes
ripd=yes
ripngd=yes
isisd=yes
```

## 1. frr-isis-point-to-point-2.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via a router `r1`. Five ping packets are sent from `h1` to `h2`, and
the success/failure of these packets is reported. This program is similar to
`ah-point-to-point-2.py` available in `examples/address-helpers`, the only
difference is that we use Intermediate System to Intermediate System (ISIS), a
dynamic routing protocol, instead of manually configuring the routes. This
program uses ISIS from Free Range Routing (FRR) suite for dynamic routing. A
new package called `RoutingHelper` is imported in this program. The routing
logs are written to files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: frr-isis-point-to-point-2.py -->

## 2. frr-isis-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. Five ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` available in `examples/address-helpers`, the only
difference is that we use Intermediate System to Intermediate System (ISIS), a
dynamic routing protocol, instead of manually configuring the routes. This
program uses ISIS from Free Range Routing (FRR) suite for dynamic routing. A
new package called `RoutingHelper` is imported in this program. The routing
logs are written to files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: frr-isis-point-to-point-3.py -->

## 3. frr-ospf-point-to-point-2.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via a router `r1`. Five ping packets are sent from `h1` to `h2`, and
the success/failure of these packets is reported. It is similar to
`ah-point-to-point-2.py` available in `examples/address-helpers`, the only
difference is that we use Open Shortest Path First (OSPF), a dynamic routing
protocol, instead of manually configuring the routes. This program uses OSPF
from Free Range Routing (FRR) suite for dynamic routing. A new package called
`RoutingHelper` is imported in this program. The routing logs are written to
files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: frr-ospf-point-to-point-2.py -->

## 4. frr-ospf-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. Five ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` available in `examples/address-helpers`, the only
difference is that we use Open Shortest Path First (OSPF), a dynamic routing
protocol, instead of manually configuring the routes. This program uses OSPF
from Free Range Routing (FRR) suite for dynamic routing. A new package called
`RoutingHelper` is imported in this program. The routing logs are written to
files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: frr-ospf-point-to-point-3.py -->

## 5. frr-rip-point-to-point-2.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via a router `r1`. Five ping packets are sent from `h1` to `h2`, and
the success/failure of these packets is reported. It is similar to
`ah-point-to-point-2.py` available in `examples/address-helpers`, the only
difference is that we use Routing Information Protocol (RIP), a dynamic routing
protocol, instead of manually configuring the routes. This program uses RIP
from Free Range Routing (FRR) suite for dynamic routing. A new package called
`RoutingHelper` is imported in this program. The routing logs are written to
files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: frr-rip-point-to-point-2.py -->

## 6. frr-rip-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. Five ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` available in `examples/address-helpers`, the only
difference is that we use Routing Information Protocol (RIP), a dynamic routing
protocol, instead of manually configuring the routes. This program uses RIP
from Free Range Routing (FRR) suite for dynamic routing. A new package called
`RoutingHelper` is imported in this program. The routing logs are written to
files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: frr-rip-point-to-point-3.py -->

## 7. frr-rip-point-to-point-multi-address.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. Five ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`frr-rip-point-to-point-3.py` available in `examples/routing/frr`, the only
difference is that we assign both IPv4 and IPv6 addresses to the interfaces.
This program uses RIP from FRR routing suite for dynamic routing. A new
package called `RoutingHelper` is imported in this program. The routing logs
are written to files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: frr-rip-point-to-point-multi-address.py -->

`Note`: The above examples can be modified to work with IPv6 addressing by
changing the IPv4 subnets to IPv6 subnets. Replace IPv4 subnets
`192.168.1.0/24`, `192.168.2.0/24` and `192.168.13.0/24` by IPv6 subnets
`2001:1::/122`, `2001:2::/122` and `2001:3::/122`, respectively.
