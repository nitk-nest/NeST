# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

""" Netperf commands """
from .exec import exec_exp_commands

# pylint: disable=too-many-arguments
def run_netperf(ns_id, netperf_options, destination_ip, test_options, ipv6, out, err):
    """
    Run netperf

    Parameters
    ----------
    ns_id : str
        network namespace to run netperf from
    netperf_options : str
        default options to run netperf command with
    destination_ip : str
        ip address of the destination namespace
    run_time : num
        total time to run netperf for
    test_options : str
        experiment related netperf options
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
            f"ip netns exec {ns_id} netperf -6 {netperf_options} "
            f"-H {destination_ip} -- {test_options}",
            stdout=out,
            stderr=err,
        )

    return exec_exp_commands(
        f"ip netns exec {ns_id} netperf -4 {netperf_options} -H {destination_ip} -- {test_options}",
        stdout=out,
        stderr=err,
    )


def run_netserver(ns_id):
    """
    Run netserver

    Parameters
    ----------
    ns_id : str
        network namespace to run netperf from

    Returns
    -------
    int
        return code of the command executed
    """
    return exec_exp_commands(f"ip netns exec {ns_id} netserver")
