NeST RELEASE NOTES
==================

This file contains NeST release notes (most recent release first).

Release 0.5-dev (Not yet available)
============================

If available, the numbers below mark the issue numbers on GitLab (prefixed by '#'),
or GitLab merge request number (prefixed by '!').

New user-visible features
-------------------------
- !153: Add support for CoAP simulation
- !243: Add support for static routing

Release 0.4.1 (Mar 14, 2022)
============================

If available, the numbers below mark the issue numbers on GitLab (prefixed by '#'),
or GitLab merge request number (prefixed by '!').

New user-visible features
-------------------------
- !213: Handled keyboard interrupts during experiment run gracefully.
- !214: Added example program for TCP Reno.
- !203: Added example programs for queue disciplines.
- !218: Added example program to demonstrate TRACE level log.

Bugs fixed
----------
- !211: Correctly set the bandwidth at the IFB device.


Release 0.4 (Feb 15, 2022)
==========================

If available, the numbers below mark the issue numbers on GitLab (prefixed by '#'),
or GitLab merge request number (prefixed by '!').

New user-visible features
-------------------------
- !121: Added option to enable/disable offloads on interfaces.
- !123: Added support for Address Helper.
- !114: Added support for Switch.
- !135: Added experiment progress bar.
- !133: Uploaded nest docker image to docker hub.
- !144: Improved X and Y axis labels in the plots.
- !163: Added Router API with IPv4 and IPv6 forwarding enabled by default.
- !181: Added destination node name in plot labels and file names.
- !190: Improved routing helper to consider nodes with one interface as hosts (by default).
- !186: Removed hierarchy from config file, making it simpler to understand.
- #143: Restructured the examples directory and respective documentation.
- !177: Updated ping to output packet information in real-time.
- !197: Added input validation for commonly used NeST APIs.

Bugs fixed
----------
- !119: Fixed erroneous filtering of duplicate logs.
- !173: Fixed log_level property not being set from config file.
- !182: Empty files are not created in experiment dump.
- !184: Fixed API breakage in LDP routing.


Release 0.3 (Apr 1, 2021)
=========================

If available, the numbers below mark the issue numbers on GitLab (prefixed by '#'),
or GitLab merge request number (prefixed by '!').

New user-visible features
-------------------------
- !49: Added FRR routing suite option
- !59, !64, !86: Added IPv6 support
- !60: Added MPLS support with static routing
- !78: Added support for Ldp dynamic routing protocol using frrouting
- !65: Added packet corruption and packet loss features
- !61: Added support for running command "inside" a node
- !79: Added support for quagga and frr logs in nest
- !63: Added User and Developer Guide in Documentation.
- !93: Completed support for UDP (Iperf3 flows are parsed and plotted)
- !96: Added support for config files

Bugs fixed
----------
- !44, !48: Loopback set up
- !47: Importing multiple config for multiple modules through a file made possible
- !51: Errors messages added for long interface names
- !92: Fixed logging error in config
- !94: Check python version in old pip version
- !100: Added log level "TRACE" to trace the iproute2 commands run.
- !91: Cleanup executed on exit from python IDE.
- !88: Fixed incorrect implementation of start and stop time of netperf flows.
- !82: Fixed bug in isis config file creation.


Release 0.2.1 (Dec 13, 2020)
============================

If available, the numbers below mark the issue numbers on GitLab (prefixed by '#'),
or GitLab merge request number (prefixed by '!').

New user-visible features
-------------------------
- !39: Added isis support in Quagga

Bugs fixed
----------
- !25: In v0.2, there was an error in parsing stats from ss tool. This has been addressed in !25.
- !35: Use agg backend for matplotlib. This is specifically for plotting graphs into files.
- !31: Config value was being stored locally in a variable. This has been fixed.
- #71: Fix Quagga issues in Arch.

Other issues addressed
----------------------
- !26: Add an unit test for experiment module. This improves test coverage from 55% to 71%.


Release 0.2 (Nov 03, 2020)
==========================

New user-visible features
-------------------------
- Added support for Dynamic routing (using Quagga).
- Added support for configuring NeST APIs.
- Plots generated made clearer by including parameter units.
- tc (traffic control) qdisc stats can be parsed for iproute2 version above 5.4.
- Logging support has been added for cleaner output from NeST.

Bugs fixed
----------
If available, the numbers below mark the issue numbers on GitLab (prefixed by '#').

- #55: Routing error in examples/dumbbell.py has been fixed.
- #40: delivery_rate and pacing_rate from ss are converted to one unit (Mbits) for plotting.
- #31: Resolved errors in Address management.
- #57: Handle different version formats of iproute2 correctly.


Release 0.1 (Jul 30, 2020)
==========================

- First beta release

New user-visible features
-------------------------
- Python APIs to create and manage network namespaces.
- APIs to add interfaces to network namespaces.
- APIs to handle address management and routing between network namespaces.
- APIs to add queuing disciplines to interfaces.
- APIs to run experiments on the built "virtual" topologies
- Support for parsing output from tools such as Netperf, ss, tc and ping.
- Create plots of statistics collected during experiment runs.
