.. SPDX-License-Identifier: GPL-2.0-only
    Copyright (c) 2019-2021 NITK Surathkal

NeST: Network Stack Tester
==========================

**NeST** is a python3 package aiding researchers and beginners alike in
emulating real-world networks. Here is a small *peak* into the APIs NeST provides::

    >>> # Create two nodes, emulating two network devices
    >>> host1 = Node("host1")
    >>> host2 = Node("host2")
    >>>
    >>> # Connect the above nodes, with eth1 and eth2 being
    >>> # respective interfaces of host1 and host2
    >>> eth1, eth2 = connect(host1, host2)
    >>>
    >>> # Assign addresses to the above two interfaces
    >>> eth1.set_address("192.168.1.1/24")
    >>> eth2.set_address("192.168.1.2/24")
    >>>
    >>> # Ping from host1 to host2!
    >>> host1.ping(eth2.address)
    === PING from host1 to 192.168.1.2 ===

    PING 192.168.1.2 (192.168.1.2) 56(84) bytes of data.
    64 bytes from 192.168.1.2: icmp_seq=1 ttl=64 time=0.060 ms
    64 bytes from 192.168.1.2: icmp_seq=2 ttl=64 time=0.095 ms
    64 bytes from 192.168.1.2: icmp_seq=3 ttl=64 time=0.056 ms
    64 bytes from 192.168.1.2: icmp_seq=4 ttl=64 time=0.083 ms
    64 bytes from 192.168.1.2: icmp_seq=5 ttl=64 time=0.063 ms

    --- 192.168.1.2 ping statistics ---
    5 packets transmitted, 5 received, 0% packet loss, time 4053ms
    rtt min/avg/max/mdev = 0.056/0.071/0.095/0.015 ms

**NeST** provides a set of APIs for:

* Creation of network testbed
* Configuration of network testbed
* Setup network experiment on the testbed
* Collection and Visualization of the data from the network experiment

NeST is officially supported for Python 3.6+.


.. toctree::
    :hidden:
    :caption: User Guide
    :maxdepth: 2

    user/install
    user/tutorial
    user/examples_index
    user/config

.. toctree::
    :hidden:
    :caption: Developer Guide
    :maxdepth: 2

    developer/introduction
    developer/architecture
    developer/unittest

.. toctree::
    :hidden:
    :caption: API Guide
    :maxdepth: 2

    api/api

.. toctree::
    :hidden:
    :caption: FAQ
    :maxdepth: 2

    faq/faq
