# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Network Namespace management"""

from .exec import exec_subprocess


def create_ns(ns_name):
    """
    Create namespace if it doesn't already exist

    Parameters
    ----------
    ns_name : str
        namespace name
    """
    exec_subprocess(f"ip netns add {ns_name}")


def delete_ns(ns_name):
    """
    Drops the namespace if it already exists.

    Parameters
    ----------
    ns_name : str
        namespace name
    """
    exec_subprocess(f"ip netns del {ns_name}")


def kill_all_processes(ns_name):
    """
    Kill all processes in a namespace

    Parameters
    ----------
    ns_name : str
        Namespace name
    """

    exec_subprocess(f"kill $(ip netns pids {ns_name})", shell=True)
