# Examples to understand the support of MPTCP in NeST

This directory contains the examples to demonstrate how MPTCP
can be used to augment TCP flows in `NeST`.

MPTCP is a transport protocol built on top of TCP that allows TCP
connections to use multiple paths to maximize resource usage and
increase redundancy.

`REFERENCES`
- [Link to the man-page.](https://man7.org/linux/man-pages/man8/ip-mptcp.8.html)
- The MPTCP v1 protocol is defined in
  [RFC 8684](https://www.rfc-editor.org/rfc/rfc8684.html).

`IMPORTANT`
- MPTCP is enabled by default on all Linux kernals > 5.6.
- For older systems, we recommend upgrading to a newer version. The development
  team has not tested their changes against the out-of-kernel implementation
  of MPTCP available [here](https://github.com/multipath-tcp/mptcp)
- The current implementation utilizes the `mptcpize` apt-package available on
  all kernels above 5.15. It is a program that enables multipath TCP on existing
  legacy services.
  [Link to the man-page.](https://manpages.ubuntu.com/manpages/jammy/man8/mptcpize.8.html)
- As MPTCP gains traction in the Linux community, and tools natively support
  MPTCP, Nest will begin their usage. At the time of writing, no public release
  of any tool (that NeST uses) does so.

`PRE-REQUISITE`  
To install `mptcpize`, run
```bash
sudo apt install mptcpize
```

`USGAGE TIPS AND DEBUGGING TOOLS FOR MPTCP IN NeST`

- ```py
  Node.add_mptcp_monitor(self)
  ```
  monitor displays creation and deletion of MPTCP connections as
  well as addition or removal of remote addresses and subflows. As far as the
  topology is concerned, the monitor is the ultimate source of truth regarding
  which subflows were setup and used during the experiment.  
  [Reference: ip-mptcp.](https://man7.org/linux/man-pages/man8/ip-mptcp.8.html)

- ```py
  config.set_value("show_mptcp_checklist", True)
  ```
  This config option is useful when experimenting with NeST. When set to True,
  NeST will match the topology against a checklist. This checklist defines the
  necessary checks that must pass if an MPTCP behaviour is to be expected from
  the topology. Note that passing all checks is not a confirmation that MPTCP
  behaviour will be seen in the experiment for sure. Following is the exhaustive
  list of checks in the checklist.
  - At least one MPTCP-enabled Flow must exist in the experiment.
  - For every MPTCP-enabled flow, the following checks are performed.
    - Source Node is MPTCP enabled.
    - Destination Node is MPTCP enabled.
    - Either of the end-nodes is multi-homed and multi-addressed.  
      See [Example 1](#1-mptcp-default-configurationpy) for definitions.
    - Atleast 1 interface on Source Node has a `subflow`/`fullmesh` MPTCP endpoint.
    - Atleast 1 interface on Destination Node has a `signal` MPTCP endpoint.

- ```py
  config.set_value("log_level", "trace")
  ```  
  This config option crates a new file called \verb|commands.sh|, listing all
  the bash commands that are executed by NeST during the runtime of the
  experiment. To evaluate the validity of our work, and to also ensure that
  all APIs work as expected, this config is the absolute source of truth as it
  reveals the exact commands run by the NeST APIs, internally.

- Be aware of the limitations of `iproute2`'s `ip route add ...` API.  
  See [Example 3](#3-mptcp-mega-dumbbellpy) for more info.

---

## 1. mptcp-default-configuration.py
This program emulates a network that connects two hosts `h1` and `h2` via two
routers R1, R2. Here, H2 is multihomed (has >=2 interfaces) and also
multiaddressed (the 2 interfaces on H2 belong to different subnets). Hence,
this topology can exhibit MPTCP behaviour if there are multiple paths between
H1 and H2.

The primary gain due to MPTCP is in throughput. This will be noticed due to
aggregation of the two subflows between R2 and H2. Due to no other congestion
zones in the network, if MPTCP works, we should see a throughput >10mbit.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: mptcp-default-configuration.py -->

## 2. mptcp-helper.py
The topology for this example is borrowed from `mptcp-default-configuration.py`.

The primary purpose of this example is to show the usage of the MPTCP helper in
NeST, and how it drastically reduces the setup effort for its users, while still
delivering the required configuratrion and results.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: mptcp-helper.py -->

## 3. mptcp-mega-dumbbell.py
This program contains a bunch of hosts. Some of these (H1, H5) are not multihomed
and multiaddressed and they cannot participate in MPTCP. Other hosts are MPTCP
capable. As a test, 2 MPTCP flows are setup as follows.
* H1 to H6
* H2 to H6

The experiment must show a notable bandwidth improvement on these flows (> 10 mbits).
The key idea of this example is to illustrate what makes a flow MPTCP capable. This
is shown by considering the 2 flows stated here, and reasoning out whether or not
they will exhibit an MPTCP behaviour. The same is then verified through experimentation.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: mptcp-mega-dumbbell.py -->
