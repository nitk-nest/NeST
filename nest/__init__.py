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

from .logging_helper import add_logging_level
from .user import User
from . import config

if os.geteuid() != 0:
    print('nest: python package requires root access', file=sys.stderr)
    sys.exit(1)

# Load default config values
config.default_value = config.import_default_config()

# Store user information for later use
if all(key in os.environ for key in ('SUDO_UID', 'SUDO_GID')):
    user_id = int(os.environ['SUDO_UID'])
    group_id = int(os.environ['SUDO_GID'])
    User(user_id, group_id)

# Set up logging
# Added to avoid exec commands being printed every time
add_logging_level('TRACE', logging.DEBUG - 1, 'trace')
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()    # Logger output will be output to stderr
ch.setLevel(config.get_value('log_level'))
logger.addHandler(ch)
formatter = logging.Formatter('[%(levelname)s] : %(message)s')
ch.setFormatter(formatter)
