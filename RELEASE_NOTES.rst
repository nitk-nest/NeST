NeST RELEASE NOTES
==================

This file contains NeST release notes (most recent release first).

Release 0.4.4 (Jan 5, 2024)
============================

If available, the numbers below mark the issue numbers on GitLab (prefixed by '#'),
or GitLab merge request number (prefixed by '!').

New user-visible features
-------------------------
- `!305`_: Added MPTCP functionality
- `!312`_, `!328`_, `#267`_, `#268`_, `#271`: Enabling video streaming (MPEG-DASH) support
- `!329`_: Added SIP emulation support

Bugs fixed
----------
- `!321`_: Dockerfile refactoring with no-cache
- `!327`_: Deprecating Quagga, MPLS Support and update base image version in Dockerfile
_ `!333`_, `#273`_: Replace Lock with RLock to avoid read race condition in TopologyMap
_ `!338`_: Fix NeST pipeline, setting XDG_RUNTIME_DIR environment

..
   Links::
.. _!305: https://gitlab.com/nitk-nest/nest/-/merge_requests/305
.. _!312: https://gitlab.com/nitk-nest/nest/-/merge_requests/312
.. _!321: https://gitlab.com/nitk-nest/nest/-/merge_requests/321
.. _!327: https://gitlab.com/nitk-nest/nest/-/merge_requests/327
.. _!328: https://gitlab.com/nitk-nest/nest/-/merge_requests/328
.. _!329: https://gitlab.com/nitk-nest/nest/-/merge_requests/329
.. _!333: https://gitlab.com/nitk-nest/nest/-/merge_requests/333
.. _!338: https://gitlab.com/nitk-nest/nest/-/merge_requests/338
.. _#267: https://gitlab.com/nitk-nest/nest/-/issues/267
.. _#268: https://gitlab.com/nitk-nest/nest/-/issues/268
.. _#271: https://gitlab.com/nitk-nest/nest/-/issues/271
.. _#273: https://gitlab.com/nitk-nest/nest/-/issues/273

Release 0.4.3 (Oct 29, 2023)
============================

If available, the numbers below mark the issue numbers on GitLab (prefixed by '#'),
or GitLab merge request number (prefixed by '!').

New user-visible features
-------------------------
- `!309`_: Added ARP functionality
- `!310`_: Added new DCTCP examples

Bugs fixed
----------
- `!315`_, `!317`_: Load seaborn-paper style from custom file

..
   Links::
.. _!309: https://gitlab.com/nitk-nest/nest/-/merge_requests/309
.. _!310: https://gitlab.com/nitk-nest/nest/-/merge_requests/310
.. _!315: https://gitlab.com/nitk-nest/nest/-/merge_requests/315
.. _!317: https://gitlab.com/nitk-nest/nest/-/merge_requests/317


Release 0.4.2 (Jun 03, 2023)
============================

If available, the numbers below mark the issue numbers on GitLab (prefixed by '#'),
or GitLab merge request number (prefixed by '!').

New user-visible features
-------------------------
- `!153`_, `!296`_: Added support for CoAP simulation
- `!154`_: Added support for multiple IPv4 and IPv6 addresses in interfaces
- `!156`_: Added support for setting TCP module parameters
- `!199`_: Added API to set duplicate packets
- `!219`_: Added iperf3 server options in Experiment API
- `!222`_: Added preload option in ping API
- `!225`_: Ensure dynamic routing works correctly with multiple ip addresses on interface
- `!231`_: Added packet-reordering API
- `!243`_: Added support for static routing
- `!246`_: Added delay distribution API
- `!250`_: Redesigned TopologyMap and made it thread-safe
- `!254`_: Added APIs to enable/disable network interfaces dynamically
- `!257`_: Added support for adding IP address to Switch
- `!270`_: Added support for BIRD routing suite
- `!280`_, `!281`_, `!282`_, `!297`_, `!298`_, `!299`_, `!311`_: Improved existing examples and added new example programs
- `!284`_: Added Iperf3 support in TCP flows

Bugs fixed
----------
- `!245`_: Fixed issue with duplicate IP forwarding
- `!255`_: Ensure Qdisc names are validated correctly
- `!264`_: Ensure TCP algorithm names are validated correctly
- `!293`_: Fixed FRR Zebra removing previously installed mulitaddress routes
- `!303`_, `#255`_: Fixed pcap file creation in capture_packets API


..
   Links::
.. _!153: https://gitlab.com/nitk-nest/nest/-/merge_requests/153
.. _!154: https://gitlab.com/nitk-nest/nest/-/merge_requests/154
.. _!156: https://gitlab.com/nitk-nest/nest/-/merge_requests/156
.. _!199: https://gitlab.com/nitk-nest/nest/-/merge_requests/199
.. _!219: https://gitlab.com/nitk-nest/nest/-/merge_requests/219
.. _!222: https://gitlab.com/nitk-nest/nest/-/merge_requests/222
.. _!225: https://gitlab.com/nitk-nest/nest/-/merge_requests/225
.. _!231: https://gitlab.com/nitk-nest/nest/-/merge_requests/231
.. _!243: https://gitlab.com/nitk-nest/nest/-/merge_requests/243
.. _!246: https://gitlab.com/nitk-nest/nest/-/merge_requests/246
.. _!250: https://gitlab.com/nitk-nest/nest/-/merge_requests/250
.. _!254: https://gitlab.com/nitk-nest/nest/-/merge_requests/254
.. _!257: https://gitlab.com/nitk-nest/nest/-/merge_requests/257
.. _!270: https://gitlab.com/nitk-nest/nest/-/merge_requests/270
.. _!280: https://gitlab.com/nitk-nest/nest/-/merge_requests/280
.. _!281: https://gitlab.com/nitk-nest/nest/-/merge_requests/281
.. _!282: https://gitlab.com/nitk-nest/nest/-/merge_requests/282
.. _!296: https://gitlab.com/nitk-nest/nest/-/merge_requests/296
.. _!297: https://gitlab.com/nitk-nest/nest/-/merge_requests/297
.. _!298: https://gitlab.com/nitk-nest/nest/-/merge_requests/298
.. _!299: https://gitlab.com/nitk-nest/nest/-/merge_requests/299
.. _!311: https://gitlab.com/nitk-nest/nest/-/merge_requests/311
.. _!284: https://gitlab.com/nitk-nest/nest/-/merge_requests/284
.. _!245: https://gitlab.com/nitk-nest/nest/-/merge_requests/245
.. _!255: https://gitlab.com/nitk-nest/nest/-/merge_requests/255
.. _!264: https://gitlab.com/nitk-nest/nest/-/merge_requests/264
.. _!293: https://gitlab.com/nitk-nest/nest/-/merge_requests/293
.. _!303: https://gitlab.com/nitk-nest/nest/-/merge_requests/303
.. _#255: https://gitlab.com/nitk-nest/nest/-/issues/255


Release 0.4.1 (Mar 14, 2022)
============================

If available, the numbers below mark the issue numbers on GitLab (prefixed by '#'),
or GitLab merge request number (prefixed by '!').

New user-visible features
-------------------------
- `!213`_: Handled keyboard interrupts during experiment run gracefully.
- `!214`_: Added example program for TCP Reno.
- `!203`_: Added example programs for queue disciplines.
- `!218`_: Added example program to demonstrate TRACE level log.

Bugs fixed
----------
- `!211`_: Correctly set the bandwidth at the IFB device.

..
   Links::
.. _!213: https://gitlab.com/nitk-nest/nest/-/merge_requests/213
.. _!214: https://gitlab.com/nitk-nest/nest/-/merge_requests/214
.. _!203: https://gitlab.com/nitk-nest/nest/-/merge_requests/203
.. _!218: https://gitlab.com/nitk-nest/nest/-/merge_requests/218
.. _!211: https://gitlab.com/nitk-nest/nest/-/merge_requests/211


Release 0.4 (Feb 15, 2022)
==========================

If available, the numbers below mark the issue numbers on GitLab (prefixed by '#'),
or GitLab merge request number (prefixed by '!').

New user-visible features
-------------------------
- `!121`_: Added option to enable/disable offloads on interfaces.
- `!123`_: Added support for Address Helper.
- `!114`_: Added support for Switch.
- `!135`_: Added experiment progress bar.
- `!133`_: Uploaded nest docker image to docker hub.
- `!144`_: Improved X and Y axis labels in the plots.
- `!163`_: Added Router API with IPv4 and IPv6 forwarding enabled by default.
- `!181`_: Added destination node name in plot labels and file names.
- `!190`_: Improved routing helper to consider nodes with one interface as hosts (by default).
- `!186`_: Removed hierarchy from config file, making it simpler to understand.
- `#143`_: Restructured the examples directory and respective documentation.
- `!177`_: Updated ping to output packet information in real-time.
- `!197`_: Added input validation for commonly used NeST APIs.

Bugs fixed
----------
- `!119`_: Fixed erroneous filtering of duplicate logs.
- `!173`_: Fixed log_level property not being set from config file.
- `!182`_: Empty files are not created in experiment dump.
- `!184`_: Fixed API breakage in LDP routing.

..
   Links::
.. _!119: https://gitlab.com/nitk-nest/nest/-/merge_requests/119
.. _!121: https://gitlab.com/nitk-nest/nest/-/merge_requests/121
.. _!123: https://gitlab.com/nitk-nest/nest/-/merge_requests/123
.. _!114: https://gitlab.com/nitk-nest/nest/-/merge_requests/114
.. _!135: https://gitlab.com/nitk-nest/nest/-/merge_requests/135
.. _!133: https://gitlab.com/nitk-nest/nest/-/merge_requests/133
.. _!144: https://gitlab.com/nitk-nest/nest/-/merge_requests/144
.. _!163: https://gitlab.com/nitk-nest/nest/-/merge_requests/163
.. _!173: https://gitlab.com/nitk-nest/nest/-/merge_requests/173
.. _!177: https://gitlab.com/nitk-nest/nest/-/merge_requests/177
.. _!181: https://gitlab.com/nitk-nest/nest/-/merge_requests/181
.. _!182: https://gitlab.com/nitk-nest/nest/-/merge_requests/182
.. _!184: https://gitlab.com/nitk-nest/nest/-/merge_requests/184
.. _!186: https://gitlab.com/nitk-nest/nest/-/merge_requests/186
.. _!190: https://gitlab.com/nitk-nest/nest/-/merge_requests/190
.. _!197: https://gitlab.com/nitk-nest/nest/-/merge_requests/197
.. _#143: https://gitlab.com/nitk-nest/nest/-/issues/143


Release 0.3 (Apr 1, 2021)
=========================

If available, the numbers below mark the issue numbers on GitLab (prefixed by '#'),
or GitLab merge request number (prefixed by '!').

New user-visible features
-------------------------
- `!49`_: Added FRR routing suite option
- `!59`_, `!64`_, `!86`_: Added IPv6 support
- `!60`_: Added MPLS support with static routing
- `!78`_: Added support for Ldp dynamic routing protocol using frrouting
- `!65`_: Added packet corruption and packet loss features
- `!61`_: Added support for running command "inside" a node
- `!79`_: Added support for quagga and frr logs in nest
- `!63`_: Added User and Developer Guide in Documentation.
- `!93`_: Completed support for UDP (Iperf3 flows are parsed and plotted)
- `!96`_: Added support for config files

Bugs fixed
----------
- `!44`_, `!48`_: Loopback set up
- `!47`_: Importing multiple config for multiple modules through a file made possible
- `!51`_: Errors messages added for long interface names
- `!92`_: Fixed logging error in config
- `!94`_: Check python version in old pip version
- `!100`_: Added log level "TRACE" to trace the iproute2 commands run.
- `!91`_: Cleanup executed on exit from python IDE.
- `!88`_: Fixed incorrect implementation of start and stop time of netperf flows.
- `!82`_: Fixed bug in isis config file creation.

..
   Links::
.. _!49: https://gitlab.com/nitk-nest/nest/-/merge_requests/49
.. _!59: https://gitlab.com/nitk-nest/nest/-/merge_requests/59
.. _!64: https://gitlab.com/nitk-nest/nest/-/merge_requests/64
.. _!86: https://gitlab.com/nitk-nest/nest/-/merge_requests/86
.. _!60: https://gitlab.com/nitk-nest/nest/-/merge_requests/60
.. _!78: https://gitlab.com/nitk-nest/nest/-/merge_requests/78
.. _!65: https://gitlab.com/nitk-nest/nest/-/merge_requests/65
.. _!61: https://gitlab.com/nitk-nest/nest/-/merge_requests/61
.. _!79: https://gitlab.com/nitk-nest/nest/-/merge_requests/79
.. _!63: https://gitlab.com/nitk-nest/nest/-/merge_requests/63
.. _!93: https://gitlab.com/nitk-nest/nest/-/merge_requests/93
.. _!96: https://gitlab.com/nitk-nest/nest/-/merge_requests/96
.. _!44: https://gitlab.com/nitk-nest/nest/-/merge_requests/44
.. _!48: https://gitlab.com/nitk-nest/nest/-/merge_requests/48
.. _!47: https://gitlab.com/nitk-nest/nest/-/merge_requests/47
.. _!51: https://gitlab.com/nitk-nest/nest/-/merge_requests/51
.. _!92: https://gitlab.com/nitk-nest/nest/-/merge_requests/92
.. _!94: https://gitlab.com/nitk-nest/nest/-/merge_requests/94
.. _!100: https://gitlab.com/nitk-nest/nest/-/merge_requests/100
.. _!91: https://gitlab.com/nitk-nest/nest/-/merge_requests/91
.. _!88: https://gitlab.com/nitk-nest/nest/-/merge_requests/88
.. _!82: https://gitlab.com/nitk-nest/nest/-/merge_requests/82


Release 0.2.1 (Dec 13, 2020)
============================

If available, the numbers below mark the issue numbers on GitLab (prefixed by '#'),
or GitLab merge request number (prefixed by '!').

New user-visible features
-------------------------
- `!39`_: Added isis support in Quagga

Bugs fixed
----------
- `!25`_: In v0.2, there was an error in parsing stats from ss tool. This has been addressed in !25.
- `!35`_: Use agg backend for matplotlib. This is specifically for plotting graphs into files.
- `!31`_: Config value was being stored locally in a variable. This has been fixed.
- `#71`_: Fix Quagga issues in Arch.

Other issues addressed
----------------------
- `!26`_: Add an unit test for experiment module. This improves test coverage from 55% to 71%.

..
   Links::
.. _!25: https://gitlab.com/nitk-nest/nest/-/merge_requests/25
.. _!35: https://gitlab.com/nitk-nest/nest/-/merge_requests/35
.. _!31: https://gitlab.com/nitk-nest/nest/-/merge_requests/31
.. _!39: https://gitlab.com/nitk-nest/nest/-/merge_requests/39
.. _!26: https://gitlab.com/nitk-nest/nest/-/merge_requests/26
.. _#71: https://gitlab.com/nitk-nest/nest/-/issues/71



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

- `#55`_: Routing error in examples/dumbbell.py has been fixed.
- `#40`_: delivery_rate and pacing_rate from ss are converted to one unit (Mbits) for plotting.
- `#31`_: Resolved errors in Address management.
- `#57`_: Handle different version formats of iproute2 correctly.

..
   Links::
.. _#55: https://gitlab.com/nitk-nest/nest/-/issues/55
.. _#40: https://gitlab.com/nitk-nest/nest/-/issues/40
.. _#31: https://gitlab.com/nitk-nest/nest/-/issues/31
.. _#57: https://gitlab.com/nitk-nest/nest/-/issues/57


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
