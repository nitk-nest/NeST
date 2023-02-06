# Examples to demonstrate the usage of Quagga Routing Suite in NeST

This directory contains the examples to demonstrate how Quagga Routing Suite
can be used for emulating dynamic routing in `NeST`.

`IMPORTANT`: Quagga module is not installed by default in Linux. Hence, before
running this program, install the Quagga module as explained below (ignore if
quagga is already installed).

Quagga can be obtained from your Linux distribution packages. For Ubuntu, run:

```shell
sudo apt install quagga quagga-doc
```

Edit `/etc/quagga/daemons` with an editor using `sudo` and turn on `zebra`,
`ospfd`, `ospf6d`, `ripd`, `ripngd` and `isisd` (by default they are disabled):

```shell
zebra=yes
ospfd=yes
ospf6d=yes
ripd=yes
ripngd=yes
isisd=yes
```

If the `/etc/quagga/daemons` file does not exist, create one and add the
following lines to the file (in the same order as shown below):

```shell
zebra=yes
bgpd=no
ospfd=yes
ospf6d=yes
ripd=yes
ripngd=yes
isisd=yes
babeld=no
```

Border Gateway Protocol (BGP) and Babel routing algorithms are not yet
supported in NeST.

`Note`: Ensure that a quagga owned directory named 'quagga' exists under
`/run`. If it does not exist, then use the following commands:

```shell
sudo mkdir /run/quagga
sudo chown quagga /run/quagga
```

## 1. quagga-isis-point-to-point-2.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via a router `r1`. Five ping packets are sent from `h1` to `h2`, and
the success/failure of these packets is reported. This program is similar to
`ah-point-to-point-2.py` available in `examples/address-helpers`, the only
difference is that we use Intermediate System to Intermediate System (ISIS),
a dynamic routing protocol, instead of manually configuring the routes. This
program uses ISIS from Quagga routing suite for dynamic routing. A new
package called `RoutingHelper` is imported in this program. The routing logs
are written to files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: quagga-isis-point-to-point-2.py -->

## 2. quagga-isis-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. Five ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` available in `examples/address-helpers`, the only
difference is that we use Intermediate System to Intermediate System (ISIS),
a dynamic routing protocol, instead of manually configuring the routes. This
program uses ISIS from Quagga routing suite for dynamic routing. A new package
called `RoutingHelper` is imported in this program. The routing logs are
written to files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: quagga-isis-point-to-point-3.py -->

## 3. quagga-ospf-point-to-point-2.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via a router `r1`. Five ping packets are sent from `h1` to `h2`, and
the success/failure of these packets is reported. It is similar to
`ah-point-to-point-2.py` available in `examples/address-helpers`, the only
difference is that we use Open Shortest Path First (OSPF), a dynamic routing
protocol, instead of manually configuring the routes. This program uses OSPF
from Quagga routing suite for dynamic routing. A new package called
`RoutingHelper` is imported in this program. The routing logs are written to
files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: quagga-ospf-point-to-point-2.py -->

## 4. quagga-ospf-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. Five ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` available in `examples/address-helpers`, the only
difference is that we use Open Shortest Path First (OSPF), a dynamic routing
protocol, instead of manually configuring the routes. This program uses OSPF
from Quagga routing suite for dynamic routing. A new package called
`RoutingHelper` is imported in this program. The routing logs are written to
files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: quagga-ospf-point-to-point-3.py -->

## 5. quagga-rip-point-to-point-2.py
This program emulates point to point networks that connect two hosts `h1`
and `h2` via a router `r1`. Five ping packets are sent from `h1` to `h2`, and
the success/failure of these packets is reported. It is similar to
`ah-point-to-point-2.py` available in `examples/address-helpers`, the only
difference is that we use Routing Information Protocol (RIP), a dynamic routing
protocol, instead of manually configuring the routes. This program uses RIP
from Quagga routing suite for dynamic routing. A new package called
`RoutingHelper` is imported in this program. The routing logs are written to
files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: quagga-rip-point-to-point-2.py -->

## 6. quagga-rip-point-to-point-3.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. Five ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`ah-point-to-point-3.py` available in `examples/address-helpers`, the only
difference is that we use Routing Information Protocol (RIP), a dynamic routing
protocol, instead of manually configuring the routes. This program uses RIP
from Quagga routing suite for dynamic routing. A new package called
`RoutingHelper` is imported in this program. The routing logs are written to
files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: quagga-rip-point-to-point-3.py -->

## 7. quagga-rip-point-to-point-multi-address.py
This program emulates point to point networks that connect two hosts `h1` and
`h2` via two routers `r1` and `r2`. Five ping packets are sent from `h1` to
`h2`, and the success/failure of these packets is reported. It is similar to
`quagga-rip-point-to-point-3.py` available in `examples/routing/quagga`, the
only difference is that we assign both IPv4 and IPv6 addresses to the
interfaces. This program uses RIP from Quagga routing suite for dynamic
routing. A new package called `RoutingHelper` is imported in this program.
The routing logs are written to files in a dedicated `logs` directory.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: quagga-rip-point-to-point-multi-address.py -->

`Note`: The above examples can be modified to work with IPv6 addressing by
changing the IPv4 subnets to IPv6 subnets. Replace IPv4 subnets
`192.168.1.0/24`, `192.168.2.0/24` and `192.168.13.0/24` by IPv6 subnets
`2001:1::/122`, `2001:2::/122` and `2001:3::/122`, respectively.
