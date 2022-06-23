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
* Bandwidth and latency are set
* Qdiscs are installed
"""

import uuid

from . import id_generator
from .address import Address, Subnet
from .interface import Interface
from .node import Node
from .router import Router
from .switch import Switch

# pylint: disable=cyclic-import
from .connect import connect


# Generate unique topology id for the *to be created* topology
TOPOLOGY_ID = uuid.uuid4().hex[:10]  # TODO: First 10 seems hacky
id_generator.IdGen(TOPOLOGY_ID)
