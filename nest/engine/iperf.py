# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""iperf commands"""

from .exec import exec_subprocess

def run_iperf_server(ns_name):
    """
    Run Iperf Server on a namesapce

    Parameters
    ----------
    ns_name : str
        name of the server namespace
    """
    #TODO: iperf3?
    exec_subprocess(f'ip netns {ns_name} iperf -s')


def run_iperf_client(ns_name, server_ip):
    """
    Run Iperf Client

    Parameters
    ----------
    ns_name : str
        name of the client namespace
    server_ip : str
        the ip of server to which it has to connect
    """
    exec_subprocess(f'ip netns {ns_name} iperf -c {server_ip}')
