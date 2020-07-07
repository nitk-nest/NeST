# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

from .node import Node, Router
from .interface import Interface, Veth, connect
from .address import Address, Subnet
from . import logging


def setup():
    """
    Setup done when nest.topology is imported

    1. Generate unique topology id for the
       'to be created' topology
    """

    # Imported within setup so that client
    # doesn't 'see' these packages
    import uuid
    from . import id_generator
    from .. import engine

    # Generate unique topology id
    topology_id = uuid.uuid4().hex[:10]  # TODO: First 10 seems hacky
    id_generator.ID_GEN(topology_id)


setup()
