# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

#!/usr/bin/env python3

import os, sys, subprocess
from nest.cmd import run_nest

if __name__ == '__main__':
    # Check if we have root access
    if os.geteuid() == 0:
        run_nest()
    else:
        # Else complain
        print("nest: Permission denied")