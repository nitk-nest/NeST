# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""ip route commands (mpls family)"""

from .exec import exec_subprocess


def add_mpls_route_push(host_name, dest_ip, next_hop_ip, label):
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
    label : str
        the label that is to be pushed onto the packet
    """
    exec_subprocess(
        f"ip netns exec {host_name} ip route add {dest_ip}"
        f" encap mpls {label} via inet {next_hop_ip}"
    )


def add_mpls_route_switch(host_name, incoming_label, next_hop_ip, outgoing_label):
    """
    Adds a route in routing table of host.

    Parameters
    ----------
    host_name : str
        name of the host namespace
    incoming_label : str
        the label that is on the packet when it arrives at the node
    next_hop_ip : str
        IP of the very next interface
    outgoing_label : str
        the label that is to be pushed onto the packet
    """
    exec_subprocess(
        f"ip netns exec {host_name} ip -f mpls route add {incoming_label}"
        f" as {outgoing_label} via inet {next_hop_ip}"
    )


def add_mpls_route_pop(host_name, incoming_label, next_hop_ip):
    """
    Adds a route in routing table of host.

    Parameters
    ----------
    host_name : str
        name of the host namespace
    next_hop_ip : str
        IP of the very next interface
    incoming_label : str
        the label that is on the packet when it arrives at the node
    """
    exec_subprocess(
        f"ip netns exec {host_name} ip -f mpls route add {incoming_label}"
        f" via inet {next_hop_ip}"
    )
