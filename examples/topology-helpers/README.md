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

## 3. gfc1-basic-example.py
This program uses the GFC-1 topology helper to create GFC-1 topology with 6 sender
nodes (`A`, `B`, `C`, `D`, `E`, `F`), 6 receiver nodes (`A`, `B`, `C`, `D`, `E`, `F`)
and 5 routers (`R1`, `R2`, `R3`, `R4`, `R5`). The flows are set up between the senders
and receivers as per the GFC-1 topology, the diagram of which is provided in the code
comments. The program demonstrates how to use the Gfc1Helper class to create the topology
with default configuration and collect qdisc statistics on specific router interfaces.
Note that two packages: `Experiment` and `Gfc1Helper` are used in this program.  

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: gfc1-basic-example.py -->

## 4. gfc1-custom-config.py
This program uses the GFC-1 topology helper to create GFC-1 topology with 6 sender
nodes (`A`, `B`, `C`, `D`, `E`, `F`), 6 receiver nodes (`A`, `B`, `C`, `D`, `E`, `F`)
and 5 routers (`R1`, `R2`, `R3`, `R4`, `R5`). The flows are set up between the senders
and receivers according to the GFC-1 topology, as depicted in the code comments.
This program is similar to `gfc1-basic-example.py` available in `examples/topology-helpers`,
but demonstrates how to use custom configuration options provided by the Gfc1Helper class.
The example shows how to customise the number and type of flows between sender and
receiver nodes, adjust flow duration, set custom qdisc and its parameters at router interfaces,
configure link attributes at interfaces, use IPv4 addressing instead of the default
IPv6 addressing, and enable routing logs.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: gfc1-custom-config.py -->

## 5. gfc2-basic-example.py
This program uses the GFC-2 topology helper to create GFC-2 topology with 12 sender
nodes (`A1`, `A2`, `A3`, `B1`, `B2`, `B3`, `C`, `D`, `E`, `F`, `G`, `H`), 8 receiver
nodes (`A`, `B`, `C`, `D`, `E`, `F`, `G`, `H`) and 7 routers (`R1`, `R2`, `R3`, `R4`,
`R5`, `R6`, `R7`,). The flows are set up between the senders and receivers as per the
GFC-2 topology, the diagram of which is provided in the code comments. The program
demonstrates how to use the Gfc2Helper class to create the topology with default
configuration and collect qdisc statistics on specific router interfaces.
Note that two packages: `Experiment` and `Gfc2Helper` are used in this program.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: gfc2-basic-example.py -->

## 6. gfc2-custom-config.py
This program uses the GFC-2 topology helper to create GFC-2 topology with 12 sender
nodes (`A1`, `A2`, `A3`, `B1`, `B2`, `B3`, `C`, `D`, `E`, `F`, `G`, `H`), 8 receiver
nodes (`A`, `B`, `C`, `D`, `E`, `F`, `G`, `H`) and 7 routers (`R1`, `R2`, `R3`, `R4`,
`R5`, `R6`, `R7`,). The flows are set up between the senders and receivers as per the
GFC-2 topology, the diagram of which is provided in the code comments. This program
is similar to `gfc2-basic-example.py` available in `examples/topology-helpers`, but
demonstrates how to use custom configuration options provided by the Gfc2Helper class.
The example shows how to customise the number and type of flows between sender and
receiver nodes, adjust flow duration, set custom qdisc and its parameters at router
interfaces, configure link attributes at interfaces, use IPv4 addressing instead of
the default IPv6 addressing, and enable routing logs.

<!-- The below snippet will render example code in docs website -->
<!-- #DOCS_INCLUDE: gfc2-custom-config.py -->
