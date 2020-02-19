# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import os, sys, uuid

from .arguments import parse
from .topology import Node, Router, Interface, Veth, connect
from .address import Address, Subnet
from .traffic_control import Qdisc, Class, Filter
from . import engine # TODO: Added for debugging, remove this
from . import id_generator
from .configuration import Configuration # TODO: Added temporarily

def run_nest():
    parse(sys.argv[1:])

# Update user information in Configuration
if all(key in os.environ for key in ('SUDO_UID', 'SUDO_GID')):
    user_id = int(os.environ['SUDO_UID'])
    group_id = int(os.environ['SUDO_GID'])
    Configuration._set_user_id(user_id)
    Configuration._set_group_id(group_id)

# Generate unique topology id
topology_id = uuid.uuid4().hex[:10] # TODO: First 10 seems hacky
id_generator.ID_GEN(topology_id)
