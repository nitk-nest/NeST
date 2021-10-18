.. SPDX-License-Identifier: GPL-2.0-only
    Copyright (c) 2019-2021 NITK Surathkal

Frequently Asked Questions
==========================

NeST always deletes the network namespaces it creates. How do I disable this?
-----------------------------------------------------------------------------

This feature can be disabled by using NeST config. Add the below lines at the
top of your NeST program::

    from nest import config

    config.set_value("delete_namespaces_on_termination", False)

Since, by default, NeST assigns "randomly" generated names to each namespace, you
might also want to add the below line in your code to disable it::

    config.set_value("assign_random_names", False)

Note that if the above line is added, then Node names must be at most 3
characters long. This is due to the limitation of naming interfaces in `ip link`
command.

How do I view the `iproute2` commands run by NeST?
--------------------------------------------------

You can enable this feature by adding the below 2 lines at the top of your
program::

    from nest import config
    config.set_value("log_level", "TRACE")

This will create a file called `commands.sh` with all the `iproute2` commands
NeST internally executes.
