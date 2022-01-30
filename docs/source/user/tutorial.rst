.. SPDX-License-Identifier: GPL-2.0-only
    Copyright (c) 2019-2021 NITK Surathkal

Tutorial
========

This section provides an in-depth explanation of the example programs available
in the examples/basic-examples directory. These examples cover some of the most
commonly used APIs in **NeST**.

Let's begin by building a simple topology with two hosts.

1. point-to-point-1.py
----------------------

This program (examples/basic-examples/point-to-point-1.py) emulates a point to
point network between two hosts ``h1`` and ``h2``. The main aim of this example
is to demonstrate the usage of basic APIs of NeST to create a network topology,
configure link attributes, assign IPv4 addresses and test the connectivity
between two hosts by sending one ping packet from ``h1`` to ``h2``. The program
outputs whether the transmission of the ping packets succeeded or failed. The
network topology is as shown below:

.. code-block:: sh

 #################################
 #       Network Topology        #
 #                               #
 #          5mbit, 5ms -->       #
 #   h1 ------------------- h2   #
 #       <-- 10mbit, 100ms       #
 #                               #
 #################################

Let's build this topology using NeST!

i) Building topology
^^^^^^^^^^^^^^^^^^^^
The first step is to import NeST::

    from nest.topology import *

The ``topology`` submodule in NeST provides APIs to build emulated network
topologies.

Next, let's create the two hosts, ``h1`` and ``h2``::

    h1 = Node("h1")
    h2 = Node("h2")

``Node`` is a class defined in NeST which emulates a node internally. Note
that ``Node`` takes a string parameter, representing the node name. Internally,
``Node`` uses network namespaces for emulation. Refer :ref:`Introduction to
Developer Docs` to know more about the internal architecture of NeST.

Now that two hosts are created, let's connect them using "virtual ethernet
devices" (veth pairs)::

    (eth1, eth2) = connect(h1, h2)

The ``connect`` API first creates a ``veth`` pair, which are the two network
interfaces connected to each other. Next, it assigns one of the interfaces to
``h1`` and the other interface to ``h2``. So, ``eth1`` interface is assigned to
``h1`` and ``eth2`` interface is assigned to ``h2``. Since ``eth1`` and
``eth2`` are two endpoints, ``h1`` and ``h2`` are now connected to each other!

The next step is to assign an IPv4 address to every interface in the network.
In this example, we assume that the IPv4 address of the network is
192.168.1.0/24, and hence, we assign the IPv4 addresses to ``eth1`` and
``eth2`` as follows::

    eth1.set_address("192.168.1.1/24")
    eth2.set_address("192.168.1.2/24")

We have assigned the address ``192.168.1.1`` to ``eth1`` and ``192.168.1.2`` to
``eth2``. The ``/24`` in the address specifies the subnet and we want both
the interfaces to be in the same subnet. The ``set_address`` API takes the
address as a string. Note that it is important to mention the subnet.

Although we have the network topology ready now, we have not configured the
characteristics of the links (such as maximum bandwidth, propagation delay)
between ``h1`` and ``h2``. So the next step in the program is to configure
the link characteristics. The following piece of code does that::

    eth1.set_attributes("5mbit", "5ms")
    eth2.set_attributes("10mbit", "100ms")

The attributes for the link from ``h1`` to ``h2`` are set at interface ``eth1``
(and vice versa). The first API call, ``eth1.set_attributes("5mbit", "5ms")``
sets the bandwidth to ``5 mbit`` and propagation delay to ``5 ms`` for the link
in the direction of ``h1`` to ``h2``.

The second API call sets the bandwidth and propagation delay for the link in
the direction of ``h2`` to ``h1``. Note that the bandwidth and propagation
delay can be asymmetric. In the real deployments, upload and download bandwidth
is not the same, and even propagation delays can vary because the forward and
reverse paths can be different.

Lastly, let's configure a ``ping`` packet to be sent from ``h1`` to ``h2``.
The ``ping`` API, by default, sends five ping packets from ``h1`` to ``h2``
and reports whether they succeeded or failed. It takes the IP address of the
destination host, as shown below::

    h1.ping(eth2.address)

We have now successfully built and configured the network topology! Let's run
the program and analyze the output.

ii) Running network experiment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The command to run this program and a sample output are shown below:

.. code-block:: console

    $ sudo python3 point-to-point-1.py

    === PING from h1 to 192.168.1.2 ===

    PING 192.168.1.2 (192.168.1.2) 56(84) bytes of data.
    64 bytes from 192.168.1.2: icmp_seq=1 ttl=64 time=210 ms
    64 bytes from 192.168.1.2: icmp_seq=2 ttl=64 time=105 ms
    64 bytes from 192.168.1.2: icmp_seq=3 ttl=64 time=105 ms
    64 bytes from 192.168.1.2: icmp_seq=4 ttl=64 time=105 ms
    64 bytes from 192.168.1.2: icmp_seq=5 ttl=64 time=105 ms

    --- 192.168.1.2 ping statistics ---
    5 packets transmitted, 5 received, 0% packet loss, time 4004ms
    rtt min/avg/max/mdev = 105.133/126.169/210.260/42.047 ms

    [INFO] : Cleaned up environment!

If you get the output similar to the one shown above, then the program ran
successfully for you!

If not, then there is likely an error in the way NeST was installed. Please
refer :ref:`Installation` and ensure that you completed all the required
steps.

When the above program is run, the required topology is created by NeST.
On exit, as the output of the program indicates, this topology is
deleted. NeST provides a ``config`` option using which the users can choose
to retain the topology, instead of deleting it, during termination. The
``config`` options supported in NeST are discussed here :ref:`Config Usage`.
