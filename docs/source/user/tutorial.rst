.. SPDX-License-Identifier: GPL-2.0-only
   Copyright (c) 2019-2021 NITK Surathkal

Tutorial
========

In this section, we shall emulate some simple topologies and run network
experiments on them using **NeST**. In doing so, we shall cover some of the most
commonly used APIs in **NeST**.

Let's begin by building a simple topology with just 2 nodes.

1. Peer-to-Peer topology (p2p)
------------------------------

Below is the ASCII representation of the topology:

.. code-block:: sh

   n1 ---- n2

Above, we have two **nodes**, ``n1`` and ``n2`` connected via an ethernet cable.
Let's build this topology using NeST!

i) Building topology
^^^^^^^^^^^^^^^^^^^^

Open a blank file in your favorite editor. You may name this file as ``p2p.py``.
In the tutorial, we shall give small snippets of code which you can copy-paste
into the editor one by one. The entire source code will be given at the end.

The very first step is to import NeST::

   from nest.experiment import *
   from nest.topology import *

The ``topology`` submodule in NeST provides APIs to build emulated network
topologies, and the ``experiment`` submodule provides APIs to run network
experiments in the emulated topologies.

Next, let's create the two nodes, ``n1`` and ``n2``::

   n1 = Node("n1")
   n2 = Node("n2")

``Node`` is a class defined in NeST which emulates a node internally.  Note that
``Node`` takes a string parameter, representing the node name.  This will be
needed later while using the experiment module.  (Internally, ``Node`` uses
network namespaces for emulation. Refer :ref:`Introduction to Developer Docs`
to know more).

Now that two nodes are created, let's connect them using "virtual ethernet
cables" (veth pairs)::

   (n1_n2, n2_n1) = connect(n1, n2)

The ``connect`` API firstly creates a ``veth`` pair, which are two network
interfaces connected to each other. Next, it assigns one of the interfaces to
``n1`` and the other interface to ``n2``. So, ``n1_n2`` interface is present in
``n1`` and ``n2_n1`` interface is in ``n2``. And since ``n1_n2`` and ``n2_n1``
are two endpoints of a virtual ethernet cable, ``n1`` and ``n2`` are now
connected to each other!

We are just one step away from sending packets between ``n1`` and ``n2``. We
will need to assign addresses to each of the interfaces first::

   n1_n2.set_address("10.0.0.1/24")
   n2_n1.set_address("10.0.0.2/24")

We have assigned address ``10.0.0.1`` to ``n1_n2`` and ``10.0.0.2`` to
``n2_n1``. The ``/24`` in the address specifies the subnet and we want
both interfaces to be in the same subnet.

And congrats, you have successfully built the topology! Let's run the
python program to verify. Save the ``p2p.py`` file, fire up your terminal
and run the below command in the same directory as the ``p2p.py`` file:

.. code-block:: console

   $ sudo python3 p2p.py
   [INFO] : Cleaned up environment!

If you get output shown above, then the program ran successfully for you!
If not, then there is likely an error in the way NeST was installed. Please
refer :ref:`Installation` and ensure that you have run all the required
steps.

When the above program was run, the required topology was created by
NeST. On exit, as the output of the program indicates, this topology is
deleted. But just creating a topology is not useful, let's
generate network traffic in this topology and visualize the various
parameters in the traffic as plots.

The ``p2p.py`` upto this point should contain the following::

   from nest.experiment import *
   from nest.topology import *

   n1 = Node("n1:)
   n2 = Node("n2")

   (n1_n2, n2_n1) = connect(n1, n2)

   n1_n2.set_address("10.0.0.1/24")
   n2_n1.set_address("10.0.0.2/24")

ii) Running network experiment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Firstly, let's set some delay and bandwidth to the link between ``n1`` and
``n2``::

   n1_n2.set_attributes("5mbit", "5ms")
   n2_n1.set_attributes("10mbit", "100ms")

The first API call, ``n1_n2.set_attributes("5mbit", "5ms")`` sets the bandwith
to be ``5 mbit`` and delay to be ``5 ms`` in the link, in the direction of
``n1`` to ``n2``.

The second API call sets the bandwidth and delay in the link, in the direction
of ``n2`` to ``n1``. Note that the bandwidth and delay need not be the same in
both directions, as in real-life scenario where download bandwidth are typically
higher than upload bandwidth.

Next, let's define a ``Flow`` object, representing the network traffic to be
generated in the topology::

   flow = Flow(n1, n2, n2_n1.address, 0, 60, 2)

The above API defines a flow between the two nodes ``n1`` and ``n2``.  The
parameters of ``Flow`` are: `source_node`, `destination_node`,
`destination_address`, `start_time`, `stop_time` and `number_of_streams`.

Hence, we have defined a flow from ``n0`` to ``n1`` for a duration of 60
seconds, starting at 0s and with 2 streams. The start time and stop time may
seem irrelevant for specifying the duration of flow, but they are useful for
scenrios where we have mutiple flows with different start and stop times.

Note that we just defined a ``Flow`` object above, it doesn't actually
create the network traffic. We shall do that below::

   exp = Experiment('tcp_2up')
   exp.add_tcp_flow(flow)

   exp.run()

First we create an ``Experiment`` object. Note that it takes in string parameter
for experiment name. We have named it as 'tcp_2up' since we are generating a
flow with 2 streams from ``n1`` to ``n2``.

Next, we add the previously defined ``flow`` object in the experiment ``exp``
using the ``add_tcp_flow`` API. Note that the default TCP congestion algorithm
used is cubic.

Finally, we run the experiment with ``exp.run()``. Now the defined flow
will run on the emulated topology. Let's run the program and check
the output we get!

The ``p2p.py`` at this point should be::

   from nest.experiment import *
   from nest.topology import *

   n1 = Node('n1')
   n2 = Node('n2')

   (n1_n2, n2_n1) = connect(n1, n2)

   n1_n2.set_address('10.0.0.1/24')
   n2_n1.set_address('10.0.0.2/24')

   n1_n2.set_attributes('5mbit', '5ms')
   n2_n1.set_attributes('10mbit', '100ms')

   flow = Flow(n1, n2, n2_n1.address, 0, 60, 2)

   exp = Experiment('tcp_2up')
   exp.add_tcp_flow(flow)

   exp.run()

Save the ``p2p.py`` file and run the below command in your terminal:

.. code-block:: console

   $ sudo python3 p2p.py

   [INFO] : Running experiment tcp_2up
   [INFO] : Running 2 netperf flows from n1 to 10.0.0.2...
   [INFO] : Running ss on nodes...
   [INFO] : Experiment complete!
   [INFO] : Parsing statistics...
   [INFO] : Output results as JSON dump
   [INFO] : Plotting results...
   [INFO] : Plotting complete!
   [INFO] : Cleaned up environment!

We have run a network experiment on our topology! You will find a folder
generated by NeST whose name looks similar to: ``tcp_2up(12-01-2021-12:29:34)_dump``.
The name will wary slightly based on the time you ran the NeST program.

Inside this folder, you will find the stats collected by NeST. The contents
of the folder should be as follows:

.. code-block:: console

   $ ls -1 tcp_2up(12-01-2021-12.29.34)_dump
   netperf/
   netperf.json
   ping/
   ping.json
   README.txt
   ss/
   ss.json
   README.txt

That's a handful of files! Among all those files, we see a file called
``README.txt``. This file describes in detail the contents of the files
in the folder. We highly urge you to read this file to get a better idea
of the stats obtained by NeST.
