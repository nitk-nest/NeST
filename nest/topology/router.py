# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""API related to router creation in topology"""

from nest.topology.node import Node


class Router(Node):
    """
    Abstraction for a Router.

    Attributes
    ----------
    name: str
        User given name for the Router.
    """

    def __init__(self, name):
        """
        Create a router with given `name`.

        Parameters
        ----------
        name: str
            The name of the router to be created
        """
        super().__init__(name)
        self.enable_ip_forwarding()
