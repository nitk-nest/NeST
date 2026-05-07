# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2024 NITK Surathkal

"""
NeST: Network Stack Tester
==========================

This is the entry point of NeST package.

Following actions are performed as part of setup, when
nest is imported:
1. Check if nest can manage network namespace
2. Store SUDO user and group id information
"""

import errno
import logging
import os
import sys
import signal

from .logging_helper import add_logging_level, get_trace_filehandler, SafeStreamHandler
from .user import User
from . import config

# Set high logging level so that logs aren't printed
# if user is not running as root
nest_logger = logging.getLogger(__name__)
nest_logger.setLevel(logging.CRITICAL)


def _test_netns_creation() -> bool:
    """
    Attempt to create a new network namespace in a forked process.

    This function uses unshare(2) in a forked process to verify sufficient privileges.
    """
    if (pid := os.fork()) == 0:
        try:
            # move child into freshly created network namespace
            os.unshare(os.CLONE_NEWNET)  # unshare(2)
        except OSError as err:
            # no manual created OSError without errno
            assert isinstance(err.errno, int), "OSError collected by Python with errno"
            os._exit(err.errno)  # pylint: disable=protected-access
        else:
            os._exit(0)  # pylint: disable=protected-access

    # collect result of child
    _, status = os.waitpid(pid, 0)
    if not os.WIFEXITED(status):
        raise RuntimeError("Testing creation of new network namespace failed")

    exit_code = os.WEXITSTATUS(status)
    # new network namespace created successfully
    if exit_code == 0:
        return True
    # no permission to create network namespace
    if exit_code == errno.EPERM:
        return False

    # child returned unexpected error
    raise OSError(exit_code, os.strerror(exit_code))


if not _test_netns_creation():
    print("nest: Unable to create network namespaces", file=sys.stderr)
    print("nest: Python package requires root access or CAP_SYS_ADMIN", file=sys.stderr)
    sys.exit(1)

# Load default config values
config.import_default_config()

# Store user information for later use
if all(key in os.environ for key in ("SUDO_UID", "SUDO_GID")):
    user_id = int(os.environ["SUDO_UID"])
    group_id = int(os.environ["SUDO_GID"])
    User(user_id, group_id)

# Set up logging
log_level = config.get_value("log_level")

# Logging level TRACE is used to output all the commands executed by engine to a file
add_logging_level("TRACE", logging.DEBUG - 1, "trace")

nest_logger.setLevel(log_level)
ch = SafeStreamHandler()  # Logger output will be output to stderr
ch.setLevel(log_level)
formatter = logging.Formatter("[%(levelname)s] : %(message)s")
ch.setFormatter(formatter)

# pylint: disable=no-member
ch.addFilter(
    lambda record: record.levelno != logging.TRACE
)  # To avoid engine commands to be printed to stdout
nest_logger.addHandler(ch)

if log_level == "TRACE":
    nest_logger.addHandler(get_trace_filehandler())

# Moving import here, since it's causing issues with running
# NeST without sudo privilege
from nest import clean_up  # # pylint: disable=wrong-import-position, wrong-import-order

# On recieving Termination signal, execute the given function
signal.signal(signal.SIGTERM, clean_up.delete_namespaces)
signal.signal(signal.SIGTERM, clean_up.delete_encoded_mpeg_dash_chunks)

# Load custom config values
config.search_config_files()
