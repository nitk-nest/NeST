# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""
NeST: Network Stack Tester
==========================

This is the entry point of NeST package.

Following actions are performed as part of setup, when
nest is imported:
1. Check if nest is run with root privileges
2. Store SUDO user and group id information
"""

import logging
import os
import sys

from .user import User

if os.geteuid() != 0:
    print('nest: python package requires root access', file=sys.stderr)
    sys.exit(1)

# Store user information for later use
if all(key in os.environ for key in ('SUDO_UID', 'SUDO_GID')):
    user_id = int(os.environ['SUDO_UID'])
    group_id = int(os.environ['SUDO_GID'])
    User(user_id, group_id)

# Logger output will be output to stderr
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
logger.addHandler(ch)
formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
ch.setFormatter(formatter)
