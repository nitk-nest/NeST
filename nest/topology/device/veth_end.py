# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""API related to creation of virtual ethernet devices in topology"""

import logging
from .device import Device

logger = logging.getLogger(__name__)


class VethEnd(Device):
    """
    This is the end of the veth created, to connect two devices

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
        Constructor of VethEnd

        Parameters
        ----------
        name : str
            Name of the interface
        node_id : str
            Id of the node that the interface belongs to
        """

        super().__init__(name, node_id)
