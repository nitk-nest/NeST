# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""iperf commands"""

from nest.engine.mptcp import mptcp_preload_string
from .exec import exec_exp_commands


def run_iperf_server(ns_name, server_options, is_mptcp, out, err):
    """
    Run Iperf Server on a namesapce

    Parameters
    ----------
    ns_name : str
        name of the server namespace
    server_options : str
        Specific options (like port_no, interval ) to run iperf3 command with
    is_mptcp : bool
        boolean to determine if connection is MPTCP enabled
    out : File
        temporary file to hold the stats
    err : File
        temporary file to hold any errors

    Returns
    -------
    int
        return code of the command executed
    """
    mptcpize_prefix = mptcp_preload_string(is_mptcp)

    # Runs server
    return_code = exec_exp_commands(
        f"{mptcpize_prefix}ip netns exec {ns_name} iperf3 -s {server_options}",
        stdout=out,
        stderr=err,
    )
    # return code 1 denotes that server is terminated at the end of experiment by cleaning process
    # so it is not an error.
    if return_code == 1:
        return_code = 0
    return return_code


# pylint: disable=too-many-arguments
def run_iperf_client(ns_name, iperf3_options, destination_ip, ipv6, is_mptcp, out, err):
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
    is_mptcp : bool
        boolean to determine if connection is MPTCP enabled
    out : File
        temporary file to hold the stats
    err : File
        temporary file to hold any errors

    Returns
    -------
    int
        return code of the command executed
    """
    mptcpize_prefix = mptcp_preload_string(is_mptcp)

    if ipv6:
        return exec_exp_commands(
            f"{mptcpize_prefix}"
            f"ip netns exec {ns_name} iperf3 -6 -c {destination_ip} {iperf3_options}",
            stdout=out,
            stderr=err,
        )

    return exec_exp_commands(
        f"{mptcpize_prefix}"
        f"ip netns exec {ns_name} iperf3 -c {destination_ip} {iperf3_options}",
        stdout=out,
        stderr=err,
    )
