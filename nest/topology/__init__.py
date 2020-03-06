# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

from .topology import Node, Router, Interface, Veth, connect
from .address import Address, Subnet
from . import logging
from ..configuration import Configuration

def setup():
    """
    Setup done when nest.topology is imported

    1. Update configuration with SUDO user and
       group id
    2. Generate unique topology id for the
       'to be created' topology
    """

    # Imported within setup so that client
    # doesn't 'see' these packages
    import os, uuid
    from . import id_generator
    from .. import engine

    # Update user information in Configuration
    if all(key in os.environ for key in ('SUDO_UID', 'SUDO_GID')):
        user_id = int(os.environ['SUDO_UID'])
        group_id = int(os.environ['SUDO_GID'])
        Configuration._set_user_id(user_id)
        Configuration._set_group_id(group_id)

    # Generate unique topology id
    topology_id = uuid.uuid4().hex[:10] # TODO: First 10 seems hacky
    id_generator.ID_GEN(topology_id, engine.log_level == 2)

setup()