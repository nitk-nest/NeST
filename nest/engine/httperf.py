# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""HTTP commands"""

from .exec import exec_exp_commands, exec_subprocess_in_background


def run_http_server(ns_name, port):
    """
    Run HTTP server on provided namespace

    Parameters
    ----------
    ns_name : str
        Name of the server namespace

    Returns
    -------
    int
        return code of the command executed
    """
    return exec_subprocess_in_background(
        f"ip netns exec {ns_name} python3 -m http.server {port}"
    )


# pylint: disable=too-many-arguments
def run_http_client(
    ns_name, destination_ip, port, num_conns, rate, additional_flags, out, err
):
    """
    Run HTTP client program - httperf

    Parameters
    ----------
    ns_name : str
        Name of the client namespace
    destination_ip : str
        IP address of the destination namespace
    port : num
        port number of the server at which the it is running
    num_conns : num
        Number of connections to be made from the client to the server totally
    rate : num
        Number of connections to be made by the client to the server per second
    additional flags : str
        added if user specified some more customizations to http flow options

    Returns
    -------
    int
        return code of the command executed
    """
    return exec_exp_commands(
        f"ip netns exec {ns_name} httperf --server={destination_ip} --num-conns={num_conns} "
        f"--rate={rate} --port={port} {additional_flags}",
        stdout=out,
        stderr=err,
    )
