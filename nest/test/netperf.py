# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# Definition of functions corresponding to tests run
# in netperf.

import subprocess
import re
import time
import json

import nest.topology.id_generator as id_generator
from .results import NetperfResults

RUNTIME = 10
INTERVAL = 0.2

NETPERF_TCP_OPTIONS = [
    "THROUGHPUT", "LOCAL_CONG_CONTROL", "REMOTE_CONG_CONTROL", "TRANSPORT_MSS", "LOCAL_TRANSPORT_RETRANS",
    "REMOTE_TRANSPORT_RETRANS", "LOCAL_SOCKET_TOS", "REMOTE_SOCKET_TOS", "DIRECTION", "ELAPSED_TIME",
    "PROTOCOL", "LOCAL_SEND_SIZE", "LOCAL_RECV_SIZE", "REMOTE_SEND_SIZE", "REMOTE_RECV_SIZE", "LOCAL_BYTES_SENT",
    "LOCAL_BYTES_RECVD", "REMOTE_BYTES_SENT", "REMOTE_BYTES_RECVD", "LOCAL_INTERFACE_NAME", "LOCAL_INTERFACE_DEVICE"
]

DEFAULT_NETPERF_OPTIONS = [
    "-P 0",                     # disable test banner
    "-4",                       # IPv4 Addresses
    "-t TCP_STREAM",            # Test type (NOTE: TCP_STREAM only for now)
    "-F /dev/urandom",          # file to transmit (NOTE: Inspired from flent)
    "-l 10",                    # Length of test (NOTE: Default 10s)
    "-D -{}".format(INTERVAL),  # generated interim results every INTERVAL secs
]


def run_test_commands(cmd, block=False):
    """
	runs the netperf or netserver command

	:param cmd: complete command to be run
	:type cmd: string
    :param block: flag to indicate whether to wait for the `cmd` output
    :type block: boolean

	:return output of the command
	"""
    proc = subprocess.Popen(
        cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if block:
        (stdout, stderr) = proc.communicate()
        return stdout.decode()    # stdout is a bytes-like object. Hence the usage of decode()


def run_netserver(ns_name):
    """
    Run netserver in `ns_name`

    :param ns_name: namespace to run server on
    :type ns_name: Namespace
    """
    cmd = 'ip netns exec {} netserver'.format(ns_name)
    run_test_commands(cmd)


def parse_stats(raw_stats, ns_name, lock):
    """
    parse netperf output

    :param raw_stats: netperf's output
    :type raw_stats: string
    :param ns_name: namespace name
    :type ns_name: string
    """

    # pattern that matches the netperf output corresponding to throughput
    throughput_pattern = r'NETPERF_INTERIM_RESULT\[\d+]=\d+\.\d+'
    throughput_stats = re.findall(throughput_pattern, raw_stats)
    # pattern to extract throughput value from the string
    extract_throughput_pattern = r'NETPERF_INTERIM_RESULT\[\d+]='
    # convert the values to float
    throughputs = [float(re.sub(extract_throughput_pattern, '', stat))
                   for stat in throughput_stats]

    # pattern that matches the netperf output corresponding to interval
    timestamp_pattern = r'NETPERF_ENDING\[\d+]=\d+\.\d+'
    timestamp_stats = re.findall(timestamp_pattern, raw_stats)
    # pattern to extract interval value from the string
    extract_interval_pattern = r'NETPERF_ENDING\[\d+]='
    # convert the values to float
    timestamps = [float(re.sub(extract_interval_pattern, '', stat))
                 for stat in timestamp_stats]

    # # convert intervals to timestamps by adding previous values in the list
    # timestamps = list(timestamps)
    # for i in range(1, len(timestamps)):
    #     timestamps[i] = timestamps[i] + timestamps[i-1]

    # a dict of the form { interval: throughput }
    stats_dict = {}

    for i in range(len(throughputs)):
        stats_dict[timestamps[i]] = throughputs[i]

    # pattern to match the interface name
    interface_pattern = r'LOCAL_INTERFACE_NAME=.+'
    interface_name_exp = re.search(interface_pattern, raw_stats).group()
    extract_interface_pattern = r'LOCAL_INTERFACE_NAME='
    interface_name = re.sub(extract_interface_pattern, '', interface_name_exp)

    lock.acquire()
    NetperfResults.add_result(interface_name, stats_dict)
    lock.release()


def run_netperf(ns_name, destination_ip, start_time, lock, run_time=10):
    """
        Run netperf in `ns_name`

        :param namespace: namespace to run netperf on
        :type namespace: Namespace
        """

    global DEFAULT_NETPERF_OPTIONS

    DEFAULT_NETPERF_OPTIONS[4] = '-l {}'.format(run_time)  # change the default runtime

    cmd = 'ip netns exec {ns_name} netperf {options} -H {destination}' \
        ' -- -k {test_options}'.format(ns_name=ns_name, options = " ".join(DEFAULT_NETPERF_OPTIONS),
                                       destination= destination_ip, test_options=",".join(NETPERF_TCP_OPTIONS))

    if(start_time != 0):
        time.sleep(start_time)
    raw_stats = run_test_commands(cmd, block=True)
    parse_stats(raw_stats, ns_name, lock)
