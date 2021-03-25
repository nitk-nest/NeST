# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""iperf commands"""

from .exec import exec_subprocess, exec_exp_commands


def run_iperf_server(ns_name):
    """
    Run Iperf Server on a namesapce

    Parameters
    ----------
    ns_name : str
        name of the server namespace
    """
    # Runs server as a daemon
    return exec_subprocess(f"ip netns exec {ns_name} iperf3 -s -D")


# pylint: disable=too-many-arguments
def run_iperf_client(ns_name, iperf3_options, destination_ip, ipv6, out, err):
    """
    Run Iperf Client

    Parameters
    ----------
    ns_name : str
        name of the client namespace
    iperf3_options : str
        Specific options (like run_time, number_of_flows) to run iperf3 command with
    destination_ip : str
        the ip of server to which it has to connect
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
            f"ip netns exec {ns_name} iperf3 -6 -u -c {destination_ip} {iperf3_options}",
            stdout=out,
            stderr=err,
        )

    return exec_exp_commands(
        f"ip netns exec {ns_name} iperf3 -u -c {destination_ip} {iperf3_options}",
        stdout=out,
        stderr=err,
    )
