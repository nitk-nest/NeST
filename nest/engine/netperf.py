# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

""" Netperf commands """
from nest.engine.mptcp import mptcp_preload_string
from .exec import exec_exp_commands

# pylint: disable=too-many-arguments
def run_netperf(
    ns_id,
    netperf_options,
    source_ip,
    destination_ip,
    test_options,
    ipv6,
    is_mptcp,
    out,
    err,
):
    """
    Run netperf

    Parameters
    ----------
    ns_id : str
        network namespace to run netperf from
    netperf_options : str
        default options to run netperf command with
    source_ip : str
        ip address of the source namespace's interface
    destination_ip : str
        ip address of the destination namespace
    run_time : num
        total time to run netperf for
    test_options : str
        experiment related netperf options
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
    source_ip_option = f"-L {source_ip}" if source_ip else ""

    if ipv6:
        return exec_exp_commands(
            f"{mptcpize_prefix}"
            f"ip netns exec {ns_id} netperf -6 {netperf_options} "
            f"-H {destination_ip} {source_ip_option} -- {test_options} ",
            stdout=out,
            stderr=err,
        )

    return exec_exp_commands(
        f"{mptcpize_prefix}"
        f"ip netns exec {ns_id} netperf -4 {netperf_options} "
        f"-H {destination_ip} {source_ip_option} -- {test_options}",
        stdout=out,
        stderr=err,
    )


def run_netserver(ns_id, is_mptcp):
    """
    Run netserver

    Parameters
    ----------
    ns_id : str
        network namespace to run netperf from
    is_mptcp : bool
        boolean to determine if connection is MPTCP enabled

    Returns
    -------
    int
        return code of the command executed
    """
    mptcp_prefix = mptcp_preload_string(is_mptcp)
    return exec_exp_commands(f"{mptcp_prefix}" f"ip netns exec {ns_id} netserver")
