# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""API related to interfaces in topology"""

import logging

from nest.input_validator import input_validator
from nest.topology.device import VethEnd
from nest import engine
from .base_interface import BaseInterface

logger = logging.getLogger(__name__)


class Interface(BaseInterface):
    """
    Abstraction for an network interface.

    Attributes
    ----------
    name : str
        User given name for the interface
    id : str
        This value is used by `engine` to create emulated interface
        entity
    node : Node
        `Node` which contains this `Interface`
    address : str/Address
        IP address assigned to this interface
    """

    @input_validator
    def __init__(self, interface_name: str):
        """
        Constructor of Interface.

        *Note*: The creation of Interface object does not
        create any devices in the interface.
        [See `create_veth_pair` method]

        Parameters
        ----------
        interface_name : str
            Name of the interface
        """

        super().__init__(interface_name, VethEnd(interface_name, None))

    @property
    def pair(self):
        """
        Get other pair for this interface (assuming veth)
        """
        return self._pair

    @pair.setter
    def pair(self, interface: "Interface"):
        """
        Setter for the other end of the interface that it is connected to

        Parameters
        ----------
        interface : Interface
            The interface to which this interface is connected to
        """
        self._pair = interface

    def __repr__(self):
        classname = self.__class__.__name__
        return f"{classname}({self.name!r})"


def create_veth_pair(interface1_name, interface2_name):
    """
    Handle creation of Veth pairs between
    `interface1_name` and `interface2_name`

    Parameters
    ----------
    interface1_name : str
            Name of one of the interfaces to be connected
    interface2_name : str
            Name of the other interface to be connected
    """

    interface1 = Interface(interface1_name)
    interface2 = Interface(interface2_name)

    interface1.pair = interface2
    interface2.pair = interface1

    # Create the veth
    engine.create_veth(interface1.id, interface2.id)

    return (interface1, interface2)
