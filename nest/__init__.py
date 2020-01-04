# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import sys
from .arguments import parse
from .topology import Node, Router, Interface, Veth, connect
from .address import Address
from . import engine # TODO: Added for debugging, remove this

def run_nest():
    parse(sys.argv[1:])

# print(Node())
    
