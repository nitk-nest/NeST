# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Entry point of NeST package"""

import os
import sys

from ._user import User

def setup():
    """
    Setup done when nest is imported.

    Following actions are performed in this function

    1. Check if nest is run with root privileges
    2. Store SUDO user and group id information

    """
    if os.geteuid() != 0:
        print('nest: python package requires root access', file=sys.stderr)
        sys.exit(1)

    # Update user information in Configuration
    if all(key in os.environ for key in ('SUDO_UID', 'SUDO_GID')):
        user_id = int(os.environ['SUDO_UID'])
        group_id = int(os.environ['SUDO_GID'])
        User(user_id, group_id)


setup()