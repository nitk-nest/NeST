# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import os
import tempfile
import time
import subprocess
import shlex
import re
from nest.experiment.results import SsResults


class SsRunner:
    """Runs ss command and stores and parses the output

    Attributes
    ----------
    iterator : str
        absolute path of the ss iterator script
    param_list: list(str)
        list of parameters to be parsed
    out : File
        temporary file to hold the stats
    ns_name : str
            network namespace to run ss from
    destination_ip : str
        ip address of the destination namespace
    start_time : num
        time at which ss is to be run
    run_time : num
        total time to run ss for
    """

    iterator = os.path.realpath(os.path.dirname(__file__)) + "/iterators/ss.sh"
    param_list = ['cwnd', 'rwnd', 'rtt', 'ssthresh',
                  'rto', 'delivery_rate', 'pacing_rate']

    def __init__(self, ns_name, destination_ip, start_time, run_time,):
        """Constructor to initialize ss runner

        Parameters
        ----------
        ns_name : str
            network namespace to run ss from
        destination_ip : str
            ip address of the destination namespace
        start_time : num
            time at which ss is to be run
        run_time : num
            total time to run ss for
        """
        self.out = tempfile.TemporaryFile()
        self.ns_name = ns_name
        self.destination_ip = destination_ip
        self.start_time = start_time
        self.run_time = run_time

    def run(self):
        """runs the ss iterator
        """
        if self.start_time != 0:
            time.sleep(self.start_time)

        command = "ip netns exec {ns_name} /bin/bash {iterator} {destination} {duration} {filter}".format(
            ns_name=self.ns_name, iterator=SsRunner.iterator, destination=self.destination_ip,
            duration=self.run_time, filter="\"dport != 12865 and sport != 12865\"")

        proc = subprocess.Popen(shlex.split(command),
                                stdout=self.out, stderr=subprocess.PIPE)

        proc.communicate()

    def parse(self):
        """parses the required data from `self.out`
        """
        stats_dict_list = {}

        self.out.seek(0)    # rewind to start of the temp file

        # See `iterators/ss.h` for output format
        raw_stats = self.out.read().decode().split("---")

        for raw_stat in raw_stats[:-1]:

            # Pattern to capture port numbers of flows to `destination ip`
            port_pattern = re.escape(self.destination_ip) + r':(?P<port>\d+)'
            port_list = [port.group('port')
                         for port in re.finditer(port_pattern, raw_stat)]
            timestamp_pattern = r'timestamp:(?P<timestamp>\d+\.\d+)'
            timestamp = re.search(
                timestamp_pattern, raw_stat).group("timestamp")
            for port in port_list:
                if port not in stats_dict_list:
                    stats_dict_list[port] = [{"timestamp": timestamp}]
                else:
                    stats_dict_list[port].append({"timestamp": timestamp})

            for param in SsRunner.param_list:
                pattern = r'\s' + \
                    re.escape(param) + \
                    r'[\s:](?P<value>\w+\.?\w*(?:[\/\,]\w+\.?\w*)*)\s'
                # result list stores all the string that is matched by the `pattern`
                param_value_list = [value.group('value')
                                    for value in re.finditer(pattern, raw_stat)]
                param_value = ''
                for i in range(len(param_value_list)):
                    param_value = param_value_list[i].strip()
                    # remove the units at the end
                    param_value = re.sub(r'[A-Za-z]', '', param_value)
                    try:
                        # rtt has both avg and dev rtt separated by a /
                        if param == 'rtt':
                            avg_rtt = param_value.split('/')[0]
                            dev_rtt = param_value.split('/')[1]
                            stats_dict_list[port_list[i]][-1]['rtt'] = avg_rtt
                            stats_dict_list[port_list[i]
                                            ][-1]['dev_rtt'] = dev_rtt
                        else:
                            stats_dict_list[port_list[i]
                                            ][-1][param] = param_value
                    except:
                        pass

        SsResults.add_result(
            self.ns_name, {self.destination_ip: stats_dict_list})
