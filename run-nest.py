# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

#!/usr/bin/env python3

import os, sys, subprocess
from nest import run_nest

if __name__ == '__main__':
    # Check if we have root access
    if os.geteuid() == 0:
        run_nest()
    else:
        # Else ask for password and rerun as root
        print("!!!Root access required!!!")
        subprocess.call(['sudo', '-k', 'python3'] + sys.argv) # "sudo -k" always prompts for password