# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Traceroute command"""

from .exec import exec_subprocess, exec_subprocess_with_live_output


# pylint: disable=too-many-arguments
def traceroute(ns_name, dest_addr, live_output=False, protocol="default", max_ttl=30):
    """
    Run traceroute between mentioned host and destination IP address

    Parameters
    ----------
    ns_name : str
        source namespace name
    dest_addr : str
        destination address for traceroute
    protocol: str
            If protocol = 'default', UDP is used. This is the default option.
            If protocol = 'icmp', use ICMP ECHO for tracerouting
            If protocol = 'tcp' TCP SYN is used for tracerouting
    max_ttl: int
        Set the maximum number of hops (max TTL to be reached)

    Returns
    -------
    bool
        success of traceroute
    """

    command = (
        f"ip netns exec {ns_name} traceroute -M {protocol} -m {max_ttl} {dest_addr}"
    )

    if live_output:
        status = exec_subprocess_with_live_output(command)
    else:
        status = exec_subprocess(command)

    return status == 0
