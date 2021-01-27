# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""IP address commands"""

from .exec import exec_subprocess


def assign_ip(host_name, dev_name, ip_address):
    """
    Assigns ip address to interface

    Parameters
    ----------
    host_name : str
        name of the host namespace
    dev_name : str
        name of the interface
    ip_address : str
        ip address to be assigned to the interface
    """
    # TODO: Support for IPv6
    exec_subprocess(
        f"ip netns exec {host_name} ip address add {ip_address} dev {dev_name}"
    )
