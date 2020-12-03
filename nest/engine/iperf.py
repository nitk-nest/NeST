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
    exec_subprocess(
        f'ip netns exec {ns_name}  iperf3 -s -D')   # runs server as a daemon


def run_iperf_client(ns_name, server_ip, run_time, flows, target_bw):
    """
    Run Iperf Client

    Parameters
    ----------
    ns_name : str
        name of the client namespace
    server_ip : str
        the ip of server to which it has to connect
    run_time : num
        test duration
    flows : int
        number of parallel flows
    target_bw : int
        target bandwidth of the UDP flow in mbits
    """

    exec_subprocess(
        f'ip netns exec {ns_name} iperf3 -u -c {server_ip} -P {flows} -t {run_time} \
            -b {target_bw}m -i 0')
