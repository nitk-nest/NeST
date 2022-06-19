# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""API related to creation of bridge in topology"""

import logging

from nest import engine
from .device import Device

logger = logging.getLogger(__name__)


class Bridge(Device):
    """
    Abstraction for a bridge.

    Attributes
    ----------
    id : str
        This value is used by `engine` to create emulated interface
        entity
    node_id : str
        id of the Node to which this Device belongs
    """

    def __init__(self, name, node_id):
        """
        Constructor of Bridge

        Parameters
        ----------
        name : str
            Name of the bridge
        node_id : str
            Id of the node that the bridge belongs to
        """
        engine.create_switch(node_id, node_id)
        engine.set_switch_mode(node_id, "up")
        super().__init__(name, node_id)
