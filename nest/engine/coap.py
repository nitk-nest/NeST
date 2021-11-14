# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""CoAP commands"""

import os

from .exec import exec_exp_commands, exec_subprocess_in_background

# pylint: disable=too-many-arguments
def run_coap_client(ns_name, destination_ip, ipv6, coap_options, out, err):
    """
    Run CoAP client program

    Parameters
    ----------
    ns_name : str
        Name of the client namespace
    destination_ip : str
        IP address of the destination namespace
    ipv6 : bool
        Indicates whether the IP address is IPv6 or not
    coap_options : str
        Options string for running the CoAP client application
    out : File
        temporary file to hold the stats
    err : File
        temporary file to hold any errors

    Returns
    -------
    int
        return code of the command executed
    """
    # Here, the path to the current file being run `coap.py` is taken
    # and used to run `coap_client.py` in the same directory. This is
    # done using the `__file__` dunder variable and the `os` library.
    path_to_curr_module = os.path.dirname(os.path.abspath(__file__))
    path_to_client = path_to_curr_module + "/coap_client.py"

    # If destination address is IPv6, check
    # if square brackets are present to use it as
    # a hostname. If not, add square brackets.
    if ipv6:
        if destination_ip[0] != "[":
            destination_ip = "[" + destination_ip + "]"

    return exec_exp_commands(
        f"ip netns exec {ns_name} python3 {path_to_client} -d {destination_ip} {coap_options}",
        stdout=out,
        stderr=err,
    )


def run_coap_server(ns_name, server_options):
    """
    Run CoAP server program

    Parameters
    ----------
    ns_name : str
        Name of the server namespace
    server_options : str
        Options string for running the server process

    Returns
    -------
    int
        return code of the command executed
    """
    # Here, the path to the current file being run `coap.py` is taken
    # and used to run `coap_server.py` in the same directory. This is
    # done using the `__file__` dunder variable and the `os` library.
    path_to_curr_module = os.path.dirname(os.path.abspath(__file__))
    path_to_server = path_to_curr_module + "/coap_server.py"

    return exec_subprocess_in_background(
        f"ip netns exec {ns_name} python3 -u {path_to_server} {server_options}",
        shell=True,
    )
