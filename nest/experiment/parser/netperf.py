# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# Definition of functions corresponding to tests run
# in netperf.

import subprocess
import re
import time
import json
import copy

from ..results import NetperfResults

RUNTIME = 10
INTERVAL = 0.2

# NOTE: LOCAL_INTERFACE_* deprecated in netperf 2.7.0
TCP_OUTPUT_OPTIONS = [
    'THROUGHPUT', 'LOCAL_CONG_CONTROL', 'REMOTE_CONG_CONTROL', 'TRANSPORT_MSS', 'LOCAL_SOCKET_TOS', 'REMOTE_SOCKET_TOS'
]

DEFAULT_NETPERF_OPTIONS = {
    'banner': '-P 0',                       # Disable test banner
    'ipv4': '-4',                         # IPv4 Addresses
    # Test type (NOTE: TCP_STREAM only for now)
    'testname': '-t TCP_STREAM',
    # File to transmit (NOTE: Inspired from flent)
    'fill_file': '-F /dev/urandom',
    # Length of test (NOTE: Default 10s)
    'testlen': '-l {}'.format(RUNTIME),
    # Generated interim results every INTERVAL secs
    'intervel': '-D -{}'.format(INTERVAL),
    'debug': '-d',                         # Enable debug mode
}

NETPERF_TCP_OPTIONS = {
    'cong_algo': '-K cubic',                   # Congestion algorithm
    'stats': '-k THROUGHPUT'               # Stats required
}

NETPERF_UDP_OPTIONS = {
    'routing': '-R 1',                       # Enable routing
    'stats': '-k THROUGHPUT'               # Stats required
}


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


def parse_stats(raw_stats, ns_name, destination_ip, lock):
    """
    parse netperf output

    :param raw_stats: netperf's output
    :type raw_stats: string
    :param ns_name: namespace name
    :type ns_name: string
    """

    # pattern that matches the netperf output corresponding to throughput
    throughput_pattern = r'NETPERF_INTERIM_RESULT\[\d+]=(?P<throughput>\d+\.\d+)'
    throughputs = [throughput.group('throughput') for throughput in re.finditer(
        throughput_pattern, raw_stats)]

    # pattern that matches the netperf output corresponding to interval
    timestamp_pattern = r'NETPERF_ENDING\[\d+]=(?P<timestamp>\d+\.\d+)'
    timestamps = [timestamp.group('timestamp') for timestamp in re.finditer(
        timestamp_pattern, raw_stats)]

    # pattern that gives the remote port
    remote_port_pattern = r'remote port is (?P<remote>\d+)'
    remote_port = re.search(remote_port_pattern, raw_stats).group('remote')

    # # convert intervals to timestamps by adding previous values in the list
    # timestamps = list(timestamps)
    # for i in range(1, len(timestamps)):
    #     timestamps[i] = timestamps[i] + timestamps[i-1]

    # a dict of the form { interval: throughput }
    stats_list = []

    for i in range(len(throughputs)):
        stats_list.append({
            'timestamp': timestamps[i],
            'throughput': throughputs[i]
        })

        stats_dict = {'{}:{}'.format(destination_ip, remote_port): stats_list}

    # pattern to match the interface name
    # interface_pattern = r'LOCAL_INTERFACE_NAME=.+'
    # interface_name_exp = re.search(interface_pattern, raw_stats).group()
    # extract_interface_pattern = r'LOCAL_INTERFACE_NAME='
    # interface_name = re.sub(extract_interface_pattern, '', interface_name_exp)

    lock.acquire()
    NetperfResults.add_result(ns_name, stats_dict)
    lock.release()


def run_netperf(ns_name, destination_ip, start_time, lock, run_time, **kwargs):
    """
    Run netperf in `ns_name`

    :param namespace: namespace to run netperf on
    :type namespace: Namespace
    :param destination_ip: IP with netserver running
    :type destination_ip: string
    :param start_time: Time to start running netperf
    :type start_time: int
    :param lock: netperf Process lock
    :type lock: Lock
    :param run_time: netperf runtime
    :type run_time: int
    :param **kwargs: netperf specific options
    :type **kwargs: dict
    """

    options = copy.copy(DEFAULT_NETPERF_OPTIONS)
    test_options = None

    # Change the default runtime
    options['testlen'] = '-l {}'.format(run_time)
    options['testname'] = '-t {}'.format(kwargs['testname'])    # Set test

    if options['testname'] == '-t TCP_STREAM':
        test_options = copy.copy(NETPERF_TCP_OPTIONS)
        test_options['cong_alg'] = '-K {}'.format(kwargs['cong_algo'])
    elif options['testname'] == '-t UDP_STREAM':
        test_options = copy.copy(NETPERF_UDP_OPTIONS)

    options_list = list(options.values())
    options_string = ' '.join(options_list)
    test_options_list = list(test_options.values())
    test_options_string = ' '.join(test_options_list)

    cmd = 'ip netns exec {ns_name} netperf {options} -H {destination} -- {test_options}'.format(
        ns_name=ns_name, options=options_string, destination=destination_ip,
        test_options=test_options_string)

    if(start_time != 0):
        time.sleep(start_time)
    raw_stats = run_test_commands(cmd, block=True)
    parse_stats(raw_stats, ns_name, destination_ip, lock)
