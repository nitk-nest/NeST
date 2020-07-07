# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal


def setup():
    """
    Setup done when nest is imported

    1. Update configuration with SUDO user and
       group id
    """

    # Imported within setup so that client
    # doesn't 'see' these packages
    import os
    import sys

    if os.geteuid() != 0:
        print('nest: python package requires root access', file=sys.stderr)
        sys.exit(1)

    from .user import User

    # Update user information in Configuration
    if all(key in os.environ for key in ('SUDO_UID', 'SUDO_GID')):
        user_id = int(os.environ['SUDO_UID'])
        group_id = int(os.environ['SUDO_GID'])
        User(user_id, group_id)


setup()
