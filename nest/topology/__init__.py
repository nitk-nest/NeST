# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""
Topology module
===============

This module is responsible for setting up an emulated topology.

In topology creation,

* Nodes are created
* Connections are made between nodes
* Addresses are assigned to interfaces
"""

import uuid

from . import id_generator
from nest import engine
from .node import Node
from .interface import Interface, Veth, connect
from .address import Address, Subnet
from . import logging


def setup():
    """
    Setup done when nest.topology is imported

    Generate unique topology id for the *to be created* topology

    """
    topology_id = uuid.uuid4().hex[:10]  # TODO: First 10 seems hacky
    id_generator.ID_GEN(topology_id)


setup()
