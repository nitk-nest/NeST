# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Ping command"""

from .exec import exec_exp_commands, exec_subprocess, exec_subprocess_with_live_output


def ping(ns_name, dest_addr, packets=1, ipv6=False, live_output=True):
    """
    Send a ping packet from ns_name to dest_addr
    if possible

    Parameters
    ----------
    ns_name : str
        namespace name
    dest_addr : str
        address to ping to
    packets : int
        Number of ping packets sent (default: 1)
    live_output : bool
        Show live output of ping packets

    Returns
    -------
    bool
        success of ping
    """
    if live_output:
        if ipv6:
            status = exec_subprocess_with_live_output(
                f"ip netns exec {ns_name} ping -6 -c {packets} {dest_addr}"
            )
        else:
            status = exec_subprocess_with_live_output(
                f"ip netns exec {ns_name} ping -c {packets} {dest_addr}"
            )
    else:
        if ipv6:
            status = exec_subprocess(
                f"ip netns exec {ns_name} ping -6 -c {packets} {dest_addr}"
            )
        else:
            status = exec_subprocess(
                f"ip netns exec {ns_name} ping -c {packets} {dest_addr}"
            )
    return status == 0


# pylint: disable=too-many-arguments
def run_exp_ping(ns_id, destination_ip, run_time, ipv6, out, err):
    """
    Run ping to extract stats

    Parameters
    ----------
    ns_id : str
        network namespace to run netperf from
    destination_ip : str
        IP address of the destination namespace
    run_time : num
        total time to run netperf for
    ipv6 : bool
        determines if destination_ip is ipv4/ipv6
    out : File
        temporary file to hold the stats
    err : File
        temporary file to hold any errors

    Returns
    -------
    int
        return code of the command executed
    """
    if ipv6:
        return exec_exp_commands(
            f"ip netns exec {ns_id} ping -6 {destination_ip} -w {run_time} -D \
            -i 0.2",
            stdout=out,
            stderr=err,
        )

    return exec_exp_commands(
        f"ip netns exec {ns_id} ping {destination_ip} -w {run_time} -D \
            -i 0.2",
        stdout=out,
        stderr=err,
    )
