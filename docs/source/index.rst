.. SPDX-License-Identifier: GPL-2.0-only
   Copyright (c) 2019-2021 NITK Surathkal

NeST: Network Stack Tester
==========================

**NeST** is a python3 package aiding researchers and beginners alike in
emulating real-world networks. Here is a small *peak* into the APIs NeST provides::

   >>> # Create two nodes, emulating two network devices
   >>> node1 = Node('node1')
   >>> node2 = Node('node2')
   >>>
   >>> # Connect the above nodes, with eth1 and eth2 being
   >>> # respective interfaces of node1 and node2
   >>> eth1, eth2 = connect(node1, node2)
   >>>
   >>> # Assign addresses to the above two interfaces
   >>> eth1.set_address('10.0.0.1/24')
   >>> eth2.set_address('10.0.0.2/24')
   >>>
   >>> # Ping between the two nodes!
   >>> node1.ping(eth2.address)  # address of eth2 in node1
   SUCCESS: ping from node1 to 10.0.0.2

**NeST** provides a set of APIs for:

* Creation of network testbed
* Configuration of network testbed
* Setup network experiment on the testbed
* Collection and Visualization of the data from the network experiment

NeST is officially supported for Python 3.6+.

------------------------------------------------------------------------

This below section contains step-by-step information to get started with
using **NeST**.

.. toctree::
   :caption: User Guide
   :maxdepth: 2

   user/install
   user/tutorial
   user/config

.. toctree::
   :caption: Developer Guide
   :maxdepth: 2

   developer/introduction
   developer/architecture

.. toctree::
   :caption: API Guide
   :maxdepth: 2

   api/api
