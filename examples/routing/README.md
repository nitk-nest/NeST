# Examples to demonstrate the support of routing in NeST

This directory contains the examples to demonstrate how dynamic routing
protocols and static routing can be used to form routes in `NeST`.

**Support of dynamic routing protocols**
`NeST` currently supports three routing suites and Multi Protocol Label
Switching (MPLS) to provide the support of dynamic routing:

- `Quagga` [[official website](https://www.quaggaproject.org/)]
- `Free Range Routing (FRR)` [[official website](https://frrouting.org/)]
- `BIRD Internet Routing Daemon (BIRD)` [[official website](https://bird.network.cz/)]
- Multi Protocol Label Switching [[overview](https://en.wikipedia.org/wiki/Multiprotocol_Label_Switching)]

`Note`: You can install either `Quagga` or `FRR` routing suite to use dynamic
routing APIs in NeST, but both cannot be installed at the same time.
The steps to install the `docker` image are provided in [Installation
instructions](https://gitlab.com/nitk-nest/nest/-/blob/master/docs/source/user/install.rst).
There are no such constraints on the installation of `BIRD` and it can be simply used in conjunction with `Quagga` or `FRR`.

**NeST passively supports quagga because it is no longer maintained by the quagga community.**
**FRR is the default in NeST. The Dockerfile will not generate an image with a quagga installation.**

There are six sub-directories inside this directory, one each for examples
related to `quagga`, `frr`, `bird`, `mpls`, `static-routing` and `print_routes_to_file()`. The necessary instructions to install
prerequisite packages are provided in separate README files in the respective
sub-directories. It is highly recommended to walk through these README files
before proceedings with the example programs.

`NeST` supports three routing protocols: Intermediate System to Intermediate
System (ISIS), Open Shortest Path First (OSPF) and Routing Information Protocol
(RIP) via both `quagga` and `frr`. In `NeST`, the `BIRD` routing suite, the `OSPF` and `RIP` routing algorithms are supported, while `ISIS` is not. Label Distribution Protocol (LDP) is
supported for label distribution in MPLS.

**Support of static routing**
NeST supports statically populating the routing tables by constructing a
spanning tree of the network using Depth First Search (DFS). No additional
libraries are required to use static routing in NeST.

<!-- The below snippet will only render in docs website -->
<!--
#BEGIN_DOCS

```{toctree}
---
---

frr/README
mpls/README
quagga/README
static-routing/README
bird/README
```

#END_DOCS
-->
