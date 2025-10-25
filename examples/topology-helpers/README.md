# Examples to demonstrate the usage of Topology Helpers in NeST

This directory contains the following examples to understand how topology
helpers can be used in `NeST` to create commonly used topologies easily.
These helpers can avoid the overhead of manually creating the devices,
creating the networks, connecting the devices, assigning addresses, setting
routing up if required and configuring the links with standard values by default.
We recommend that you walk through these examples in the same order as they
are presented.

## 1. dumbbell-basic-example.py
This program uses the dumbbell topology helper to create a dumbbell topology
with three left nodes (`lh1`, `lh2`, and `lh3`), four right nodes (`rh1`, `rh2`,
`rh3`, and `rh4`) connected by two routers (`r1` and `r2`) in the middle. Four
flows are set up: one TCP flow from `lh1` to `rh1`, one TCP flow from `lh2` to
`rh2`, one TCP flow from `lh3` to `rh3`, and one UDP flow from `lh3` to `rh4`.
This program shows how the dumbbell helper can be used with default configurations
and how the instance variables and methods of the object of this helper can be
used to access the components (like nodes, interfaces, etc.) of the network
topology created. Note that three packages: `Experiment`, `Flow` and
`DumbbellHelper` are imported in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: dumbbell-basic-example.py -->

## 2. dumbbell-custom-config.py
This program uses the dumbbell topology helper to create a dumbbell topology
with three left nodes (`lh1`, `lh2`, and `lh3`), four right nodes (`rh1`, `rh2`,
`rh3`, and `rh4`) connected by two routers (`r1` and `r2`) in the middle. Four
flows are set up: one TCP flow from `lh1` to `rh1`, one TCP flow from `lh2` to
`rh2`, one TCP flow from `lh3` to `rh3`, and one UDP flow from `lh3` to `rh4`.
This program is similar to `dumbbell-basic-example.py` available in
`examples/topology-helpers`, the only difference is that we have shown how the
address family used can be changed from the default of IPv6 to IPv4, how FRR
logging can be enabled, and how interface attributes like bandwidth, delay and
qdisc (along with qdisc parameters) can be changed. Note that three packages:
`Experiment`, `Flow` and `DumbbellHelper` are imported in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: dumbbell-custom-config.py -->
