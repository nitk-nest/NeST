# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019 NITK Surathkal

import sys
from .arguments import parse

def run_nest():
    parse(sys.argv[1:])


    