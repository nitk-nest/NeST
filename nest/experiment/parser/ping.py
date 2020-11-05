# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Runs and provides RTT output from ping command"""

import re
from time import sleep
from .runnerbase import Runner
from ..results import PingResults
from ...topology_map import TopologyMap


class PingRunner(Runner):
    """
    Runs ping command and parses statistics from its output

    Attributes
    ----------
    ns_id : str
        network namespace to run netperf from
    destination_ip : str
        IP address of the destination namespace
    start_time : num
        time at which netperf is to run
    run_time : num
        total time to run netperf for
    """

    def __init__(self, ns_id, destination_ip, start_time, run_time):
        """
        Constructor to initialize ping runner

        Parameters
        ----------
        ns_id : str
            network namespace to run netperf from
        destination_ip : str
            IP address of the destination namespace
        start_time : num
            time at which netperf is to run
        run_time : num
            total time to run netperf for
        """
        self.ns_id = ns_id
        self.destination_ip = destination_ip
        super().__init__(start_time, run_time)

    # pylint: disable=arguments-differ
    def run(self):
        """
        Runs ping at t=`self.start_time`
        """
        if self.start_time > 0:
            sleep(self.start_time)
        command = f'ip netns exec {self.ns_id} ping {self.destination_ip} -w {self.run_time} -D \
            -i 0.2'
        super().run(command)

    def print_error(self):
        """
        Method to print error from `self.err`
        """
        self.err.seek(0)  # rewind to start of file
        error = self.err.read().decode()
        ns_name = TopologyMap.get_namespace(self.ns_id)['name']
        self.logger.error('Collecting latency at %s. %s', ns_name, error)

    def parse(self):
        """
        parses the RTT from `self.out`
        """
        self.out.seek(0)    # rewind to start of the temp file
        raw_stats = self.out.read().decode()

        pattern = r'\[(?P<timestamp>\d+\.\d+)\].*time=(?P<rtt>\d+(\.\d+)?)'
        timestamps_and_rtts = [(match.group('timestamp'), match.group(
            'rtt')) for match in re.finditer(pattern, raw_stats)]

        # List storing collected stats
        # First item as "meta" item with user given information
        stats_list = [self.get_meta_item()]

        for (timestamp, rtt) in timestamps_and_rtts:
            stats_list.append({
                'timestamp': timestamp,
                'rtt': rtt
            })

        stats_dict = {self.destination_ip: stats_list}

        PingResults.add_result(self.ns_id, stats_dict)
