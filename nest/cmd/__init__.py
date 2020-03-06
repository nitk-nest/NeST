# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import sys
from .arguments import parse, run_args

def run_nest():
    """
    Parses the args passed to nest command
    and executes the requested tasks.
    If there are error in flags, then display
    necessary error message.
    """

    arguments = parse(sys.argv[1:])
    run_args(arguments)