# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import sys
from .arguments import parse_nest

def run_nest():

    parse_nest(sys.argv[1:])