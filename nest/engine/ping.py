# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Ping command"""

from .exec import exec_subprocess

def ping(ns_name, dest_addr):
    """
    Send a ping packet from ns_name to dest_addr
    if possible

    Parameters
    ----------
    ns_name : str
        namespace name
    dest_addr : str
        address to ping to

    Returns
    -------
    bool
        success of ping
    """
    status = exec_subprocess(f'ip netns exec {ns_name} ping -c1 -q {dest_addr}')
    return status == 0
