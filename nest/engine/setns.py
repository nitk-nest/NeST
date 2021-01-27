# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal

"""
Run commands inside a network namespace

Inspired from: https://github.com/larsks/python-netns
"""

import os
from ctypes import CDLL, get_errno

CLONE_NEWNET = 0x40000000


def _errcheck(ret, _func, _args):
    if ret == -1:
        err = get_errno()
        raise OSError(err, os.strerror(err))


libc = CDLL("libc.so.6", use_errno=True)
libc.setns.errcheck = _errcheck


def get_ns_path(ns_name):
    """
    Get path to network namespace.

    Parameters
    ----------
    ns_name : str
        namespace name
    """
    ns_path = f"/var/run/netns/{ns_name}"

    if not os.path.exists(ns_path):
        raise ValueError(f"Network namespace path {ns_path} does not exist")

    return ns_path


def set_ns(ns_name=None):
    """
    Change the network namespace of the calling thread.

    If ns_name is None, then default namespace is assumed.

    Parameters
    ----------
    ns_name : str/None
        namespace name
    """
    ns_path = None

    if ns_name is None:
        # Default namespace, set ns_path to init process network namespace
        ns_path = "/proc/1/ns/net"
    else:
        ns_path = get_ns_path(ns_name)

    with open(ns_path) as file:
        fd = file.fileno()  # pylint: disable=invalid-name
        libc.setns(fd, CLONE_NEWNET)
