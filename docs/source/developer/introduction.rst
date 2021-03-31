.. SPDX-License-Identifier: GPL-2.0-only
   Copyright (c) 2019-2021 NITK Surathkal

Introduction to Developer docs
==============================

Developer docs is primarily for developers interested in contributing to NeST.
It gives a peak into the internal structure of NeST that can be useful for
new contributors.

Before we proceed, let's clear one thing. NeST is a wrapper around linux
network namespaces and various other networking utilities.

For network namespaces, it provides APIs to:

1. Create network namespaces
2. Add network interfaces to namespaces
3. Assign addresses to interfaces
4. Add routes in interfaces, etc

In NeST, we abstract upon network namespaces and instead call them ``Node``.
This is done so that users don't need to know about network namespaces to use
NeST.

Using the above APIs, users can build complex network topologies. NeST provides
APIs over various network utilities like ``netperf``, ``iperf3``, ``ping``, etc
so that users can run network traffic on their built topologies. These APIs
allow users to run network experiments on their built topologies. And, NeST uses
``iproute2`` tools like ``ss`` (socket stats), ``tc`` (traffic control) so that
users can obtain stats and plots from the network experiment they run.
