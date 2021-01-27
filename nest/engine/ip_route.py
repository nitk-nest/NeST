# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""IP route commands"""

from .exec import exec_subprocess


def add_route(host_name, dest_ip, next_hop_ip, via_int):
    """
    Adds a route in routing table of host.

    Parameters
    ----------
    host_name : str
        name of the host namespace
    dest_ip : str
        the destination ip for the route
    next_hop_ip : str
        IP of the very next interface
    via_int : str
        the corresponding interface in the host
    """
    exec_subprocess(
        f"ip netns exec {host_name} ip route add {dest_ip}"
        f" via {next_hop_ip} dev {via_int}"
    )
