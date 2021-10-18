.. SPDX-License-Identifier: GPL-2.0-only
    Copyright (c) 2019-2021 NITK Surathkal

.. highlight:: console

Unit tests
==========

Unit tests can be found in NeST repo at `nest/tests <https://gitlab.com/nitk-nest/nest/-/tree/master/nest/tests>`_.
They are crucial for ensuring that NeST is working as expected and are run in
GitLab CI pipeline for every MR (Merge Request). This ensures that new code changes
don't break existing APIs. Typically, each file in `nest/tests` contain unit tests
testing a certain module. E.g., `test_topology.py <https://gitlab.com/nitk-nest/nest/-/blob/master/nest/tests/test_topology.py>`_
contains unit tests for the `topology` module.

Running unit tests
------------------

Fire up your terminal and cd into the nest repo folder. Run the below command
to run all unit tests in NeST::

    $ sudo python3 -m unittest

This can take a while to run and may give errors in case you don't have some
dependencies installed. You won't be using this command most of the time
since you will be interested in only running specific unit tests. Let's say
you are interested in running unit tests for the topology module. The command for
this is::

    $ sudo python3 -m unittest nest/tests/test_topology.py

It is also possible to directly run the file::

    $ sudo python3 nest/tests/test_topology.py

Understanding how unit tests are written
----------------------------------------

We use the `unittest <https://docs.python.org/3/library/unittest.html>`_ module
in python to write our unit tests.

Open `nest/tests/test_topology.py <https://gitlab.com/nitk-nest/nest/-/blob/master/nest/tests/test_topology.py>`_
in your favorite text editor. It contains a class called `TestTopology` which
inherits `unittest.TestCase`. This class contains test methods like `test_p2p`,
`test_prp` etc., to name a few. Each of the test methods contains one unit test.

E.g., the `test_p2p` method builds a simple peer-to-peer network and checks if
the APIs involved in building this topology are working as expected. The `assert`
statements catch errors if any. The below command runs only the `test_p2p` unit test::

    $ sudo python3 -m unittest nest.tests.test_topology.TestTopology.test_p2p

The `setUp` and `tearDown` methods are part of the "test fixture". The `setUp` method
is run before every unit test and `tearDown` method is run after every unit test.
