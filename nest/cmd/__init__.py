# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import sys
from .arguments import parse, run_args

# NOTE: nest cmd support is removed for now
# Support maybe added later

def run_nest():
    """
    Parses the args passed to nest command
    and executes the requested tasks.
    If there are error in flags, then display
    necessary error message.
    """

    raise NotImplementedError("Running nest in command line is not \
            supported right now.")

    arguments = parse(sys.argv[1:])
    run_args(arguments)