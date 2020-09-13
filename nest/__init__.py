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

# See: https://stackoverflow.com/a/35804945


def add_logging_level(level_name, level_num, method_name=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not method_name:
        method_name = level_name.lower()

    if hasattr(logging, level_name):
        raise AttributeError(
            '{} already defined in logging module'.format(level_name))
    if hasattr(logging, method_name):
        raise AttributeError(
            '{} already defined in logging module'.format(method_name))
    if hasattr(logging.getLoggerClass(), method_name):
        raise AttributeError(
            '{} already defined in logger class'.format(method_name))

    def log_for_level(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            # pylint: disable=protected-access
            self._log(level_num, message, args, **kwargs)

    def log_to_root(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    logging.addLevelName(level_num, level_name)
    setattr(logging, level_name, level_num)
    setattr(logging.getLoggerClass(), method_name, log_for_level)
    setattr(logging, method_name, log_to_root)


if os.geteuid() != 0:
    print('nest: python package requires root access', file=sys.stderr)
    sys.exit(1)

# Store user information for later use
if all(key in os.environ for key in ('SUDO_UID', 'SUDO_GID')):
    user_id = int(os.environ['SUDO_UID'])
    group_id = int(os.environ['SUDO_GID'])
    User(user_id, group_id)
# Set up logging
add_logging_level('TRACE', logging.DEBUG - 1, 'trace')
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()    # Logger output will be output to stderr
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)
formatter = logging.Formatter('[%(levelname)s] : %(message)s')
ch.setFormatter(formatter)
