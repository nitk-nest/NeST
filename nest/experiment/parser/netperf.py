# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import re
import time
import copy
from ..results import NetperfResults
from ...engine import exec_exp_commands
from .runnerbase import Runner
from ...topology_map import TopologyMap

class NetperfRunner(Runner):
    """
    Runs netperf command and parses statistics from it's output

    Attributes
    ----------
    default_netperf_options : dict
        default options to run netperf command with
    netperf_tcp_options : dict
        tcp related netperf options
    netperf_udp_options : dict
        udp related netperf options
    ns_id : str
        network namespace to run netperf from
    destination_ip : str
        ip address of the destination namespace
    start_time : num
        time at which netperf is to run
    run_time : num
        total time to run netperf for
    """

    tcp_output_options = [
        'THROUGHPUT', 'LOCAL_CONG_CONTROL', 'REMOTE_CONG_CONTROL', 'TRANSPORT_MSS',
        'LOCAL_SOCKET_TOS', 'REMOTE_SOCKET_TOS'
    ]

    default_netperf_options = {
        'banner': '-P 0',                           # Disable test banner
        'ipv4': '-4',                               # IPv4 Addresses
        # Test type (NOTE: TCP_STREAM only for now)
        'testname': '-t TCP_STREAM',
        # File to transmit (NOTE: Inspired from flent)
        'fill_file': '-F /dev/urandom',
        # Length of test (NOTE: Default 10s)
        'testlen': '-l {}'.format(10),
        # Generated interim results every INTERVAL secs
        'intervel': '-D -{}'.format(0.2),
        'debug': '-d',                              # Enable debug mode
    }

    netperf_tcp_options = {
        'cong_algo': '-K cubic',                    # Congestion algorithm
        'stats': '-k THROUGHPUT'                    # Stats required
    }

    netperf_udp_options = {
        'routing': '-R 1',                          # Enable routing
        'stats': '-k THROUGHPUT'                    # Stats required
    }

    def __init__(self, ns_id, destination_ip, start_time, run_time, **kwargs):
        """
        Constructor to initialize netperf runner

        Parameters
        ----------
        ns_id : str
            network namespace to run netperf from
        destination_ip : str
            ip address of the destination namespace
        start_time : num
            time at which netperf is to run
        run_time : num
            total time to run netperf for
        **kwargs
            netperf options to override
        """
        self.ns_id = ns_id
        self.destination_ip = destination_ip
        self.start_time = start_time
        self.run_time = run_time
        self.options = copy.deepcopy(kwargs)
        super().__init__()

    # Should this be placed somewhere else?
    @staticmethod
    def run_netserver(ns_id):
        """
        Run netserver in `ns_id`

        Parameters
        ----------
        ns_id : str
            namespace to run netserver on
        """
        command = 'ip netns exec {} netserver'.format(ns_id)
        return_code = exec_exp_commands(command)
        ns_name = TopologyMap.get_namespace(ns_id)['name']
        if return_code != 0:
            print("Error running netserver at {}.".format(
                ns_name))

    def run(self):
        """
        Runs netperf at t=`self.start_time`
        """
        netperf_options = copy.copy(NetperfRunner.default_netperf_options)
        test_options = None

        # Change the default runtime
        netperf_options['testlen'] = '-l {}'.format(self.run_time)
        # Set test
        netperf_options['testname'] = '-t {}'.format(self.options['testname'])

        if netperf_options['testname'] == '-t TCP_STREAM':
            test_options = copy.copy(NetperfRunner.netperf_tcp_options)
            test_options['cong_alg'] = '-K {}'.format(
                self.options['cong_algo'])
        elif netperf_options['testname'] == '-t UDP_STREAM':
            test_options = copy.copy(NetperfRunner.netperf_udp_options)

        netperf_options_list = list(netperf_options.values())
        netperf_options_string = ' '.join(netperf_options_list)
        test_options_list = list(test_options.values())
        test_options_string = ' '.join(test_options_list)

        command = 'ip netns exec {ns_id} netperf {options} -H {destination} -- {test_options}'.format(
            ns_id=self.ns_id, options=netperf_options_string, destination=self.destination_ip,
            test_options=test_options_string)

        if self.start_time != 0:
            time.sleep(self.start_time)

        super().run(command)

    def print_error(self):
        """
        Method to print error from `self.err`
        """
        self.err.seek(0)    #rewind to start of file
        error = self.err.read().decode()
        ns_name = TopologyMap.get_namespace(self.ns_id)['name']
        print('Error running netperf at {}. {}'.format(ns_name, error))

    def parse(self):
        """
        Parse netperf output from `self.out`
        """
        self.out.seek(0)    # rewind to start of the temp file
        raw_stats = self.out.read().decode()

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

        stats_list = []

        for i in range(len(throughputs)):
            stats_list.append({
                'timestamp': timestamps[i],
                'throughput': throughputs[i]
            })

            stats_dict = {'{}:{}'.format(
                self.destination_ip, remote_port): stats_list}

        NetperfResults.add_result(self.ns_id, stats_dict)
        self.clean_up()

    def clean_up(self):
        """
        Closes the temp files created
        """
        return super().clean_up()
