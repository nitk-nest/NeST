# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""API related to switch creation in topology"""

import logging

from nest import engine
from nest.topology.node import Node

logger = logging.getLogger(__name__)


class Switch(Node):
    """
    Abstraction for a switch.

    Attributes
    ----------
    name: str
        User given name for the switch.
    """

    def __init__(self, name):
        """
        Create a switch with given `name` inside a 'Node'.

        A namespace is created by inheriting the "Node" class and unique id is given
        to the namespace. Then a switch with the same name and unique id as namespace
        is created inside the created namespace.

        Parameters
        ----------
        name: str
            The name of the switch to be created
        """
        super().__init__(name)
        engine.create_switch(self.id, self.id)
        engine.set_switch_mode(self.id, "up")

    def _add_interface(self, interface):
        """
        Add `interface` to `Switch`

        Parameters
        ----------
        interface: Interface
            `Interface` to be added to `Switch`
        """
        super()._add_interface(interface)
        engine.add_int_to_switch(self.id, interface.id)
