# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# Definition of functions corresponding to tests run
# in netperf.

import subprocess

NETPERF_TCP_OPTIONS = [
    "THROUGHPUT", "LOCAL_CONG_CONTROL", "REMOTE_CONG_CONTROL", "TRANSPORT_MSS", "LOCAL_TRANSPORT_RETRANS",
    "REMOTE_TRANSPORT_RETRANS", "LOCAL_SOCKET_TOS", "REMOTE_SOCKET_TOS", "DIRECTION","ELAPSED_TIME",
    "PROTOCOL", "LOCAL_SEND_SIZE", "LOCAL_RECV_SIZE", "REMOTE_SEND_SIZE", "REMOTE_RECV_SIZE", "LOCAL_BYTES_SENT",
    "LOCAL_BYTES_RECVD", "REMOTE_BYTES_SENT", "REMOTE_BYTES_RECVD"
]

DEFAULT_NETPERF_OPTIONS = [
    "-P 0",             # disable test banner
    "-4",               # IPv4 Addresses
    "-t TCP_STREAM",    # Test type (NOTE: TCP_STREAM only for now)
    "-F /dev/urandom",  # file to transmit (NOTE: Inspired from flent)
    "-l 10",            # Length of test (NOTE: Assumed 10s for now)
]

def run_test_commands(cmd):
    proc = subprocess.Popen(
        cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def run_netserver(ns_name):
    """
        Run netserver in `ns_name`

        :param ns_name: namespace to run server on
        :type ns_name: Namespace
        """
    cmd = 'ip netns exec {} netserver'.format(ns_name)
    run_test_commands(cmd)

def run_netperf(ns_name, destination_ip):
    """
        Run netperf in `ns_name`

        :param namespace: namespace to run netperf on
        :type namespace: Namespace
        """

    cmd = 'ip netns exec {ns_name} netperf {options} -H {destination}' \
        ' -- -k {test_options}'.format(ns_name = ns_name, options = " ".join(DEFAULT_NETPERF_OPTIONS),
        destination = destination_ip, test_options=",".join(NETPERF_TCP_OPTIONS))
    run_test_commands(cmd)