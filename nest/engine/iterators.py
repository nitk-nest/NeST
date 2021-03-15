# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

""" exectute iterator scripts """
from .exec import exec_exp_commands

# pylint: disable=too-many-arguments
def run_ss(
    ns_id, iterator, destination_ip, duration, ss_filter, start_time, ipv6, out, err
):
    """
    Executes the ss iterator script

    Parameters
    ----------
    ns_id : str
        namespace name
    iterator : str
        absolute path of the ss iterator script
    destination_ip : str
        IP address of the destination namespace
    duration : num
        total time to run ss for
    start_time : num
        time at which ss is to be run
    ss_filter : str
        filter to remove unnecessary output from ss
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
            f"ip netns exec {ns_id} /bin/bash {iterator} [{destination_ip}] \
                                    {duration} {ss_filter}  {start_time}",
            stdout=out,
            stderr=err,
        )

    return exec_exp_commands(
        f"ip netns exec {ns_id} /bin/bash {iterator} {destination_ip} \
                                {duration} {ss_filter}  {start_time}",
        stdout=out,
        stderr=err,
    )


# pylint: disable=too-many-arguments
def run_tc(ns_id, iterator, dev, duration, out, err):
    """
    Executes the tc iterator script

    Parameters
    ----------
    ns_id : str
        network namespace to run tc from
    iterator : str
        absolute path of the tc iterator script
    dev : str
        dev id to collect tc stats from
    duration : num
        total time to run tc for
    out : File
        temporary file to hold the stats
    err : File
        temporary file to hold any errors

    Returns
    -------
    int
        return code of the command executed
    """
    return exec_exp_commands(
        f"ip netns exec {ns_id} /bin/bash {iterator} {dev} {duration}",
        stdout=out,
        stderr=err,
    )
