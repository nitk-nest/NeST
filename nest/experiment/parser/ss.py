# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""
Runs ss command and parses socket stats from
its output
"""

import os
import re
from ..results import SsResults
from .runnerbase import Runner
from ...topology_map import TopologyMap


class SsRunner(Runner):
    """
    Runs ss command and stores and parses the output

    Attributes
    ----------
    iterator : str
        absolute path of the ss iterator script
    param_list: list(str)
        list of parameters to be parsed
    ns_id : str
        network namespace to run ss from
    destination_ip : str
        IP address of the destination namespace
    start_time : num
        time at which ss is to be run
    run_time : num
        total time to run ss for
    """

    iterator = os.path.realpath(os.path.dirname(__file__)) + "/iterators/ss.sh"
    param_list = ['cwnd', 'rwnd', 'rtt', 'ssthresh',
                  'rto', 'delivery_rate', 'pacing_rate']

    def __init__(self, ns_id, destination_ip, start_time, run_time):
        """
        Constructor to initialize ss runner

        Parameters
        ----------
        ns_id : str
            network namespace to run ss from
        destination_ip : str
            IP address of the destination namespace
        start_time : num
            time at which ss is to be run
        run_time : num
            total time to run ss for
        """
        self.ns_id = ns_id
        self.destination_ip = destination_ip
        super().__init__(start_time, run_time)

    def run(self):
        """
        Runs the ss iterator
        """

        command = 'ip netns exec {ns_id} /bin/bash {iterator} {destination} {duration}\
            {filter}  {start_time}'.format(
                ns_id=self.ns_id, iterator=SsRunner.iterator, destination=self.destination_ip,
                duration=self.run_time, filter="\"dport != 12865 and sport != 12865\"",
                start_time=self.start_time)

        super().run(command)

    def print_error(self):
        """
        Method to print error from `self.err`
        """
        self.err.seek(0)  # rewind to start of file
        error = self.err.read().decode()
        ns_name = TopologyMap.get_namespace(self.ns_id)['name']
        self.logger.error('Collecting socket stats at %s. %s', ns_name, error)

    # pylint: disable=too-many-locals
    def parse(self):
        """
        parses the required data from `self.out`
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
                # If port encountered first time
                if port not in stats_dict_list:
                    stats_dict_list[port] = [self.get_meta_item()]

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
                    # remove the (rate) units at the end and convert
                    if param_value.endswith('bps'):
                        param_value = self.convert_to(param_value)
                    try:
                        # RTT has both average and RTT deviation separated by a /
                        if param == 'rtt':
                            avg_rtt = param_value.split('/')[0]
                            dev_rtt = param_value.split('/')[1]
                            stats_dict_list[port_list[i]][-1]['rtt'] = avg_rtt
                            stats_dict_list[port_list[i]
                                            ][-1]['dev_rtt'] = dev_rtt
                        else:
                            stats_dict_list[port_list[i]][-1][param] = param_value
                    except TypeError:
                        pass

        SsResults.add_result(
            self.ns_id, {self.destination_ip: stats_dict_list})

    @staticmethod
    def convert_to(param_value, unit_out='Mbps'):
        """
        Converts parameter value to specified unit [For bit per second]
        """
        converter = {'bps': 1, 'Kbps': 1e3, 'Mbps': 1e6, 'Gbps': 1e9}

        # Extract value and unit
        unit_in = re.sub(r'^\d*\.?\d*', '', param_value)
        extracted_param_value = float(re.sub(r'[A-Za-z]*', '', param_value))

        converted_param_value = str(extracted_param_value * converter[unit_in]/converter[unit_out])
        return converted_param_value
