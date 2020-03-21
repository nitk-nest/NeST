# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import json
import time
from multiprocessing import Manager


class SsResults:
    """
    This class aggregates the ss stats from the entire test environment
    """

    # a shared dict for the ss processes to add their results
    # the dict is of the form { ns_name: list of ss statistics for each flow in the namespace }
    ss_results = Manager().dict()  

    @staticmethod
    def add_result(ns_name, result):
        """
        Adds the ss stats parse from a process to the shared `ss_results`
        :param ns_name: namespace name
        :type ns_name: string
        :param result: parsed ss stats
        :type result: dict
        """
        if ns_name in SsResults.ss_results:
            SsResults.ss_results[ns_name].append(result)
        else:
            SsResults.ss_results[ns_name] = [result]


    @staticmethod
    def output_to_file():
        """
        Outputs the aggregated ss stats to file
        """
        json_stats = json.dumps(SsResults.ss_results.copy(), indent=4)
        timestamp = time.strftime("%d-%m-%Y-%H:%M:%S")
        filename = str(timestamp) + ' ss-parse-results.json'
        with open(filename, 'w') as f:
            f.write(json_stats)

class NetperfResults:
    """
    This class aggregates the netperf stats from the entire test environment
    """

    
    netperf_results = Manager().dict()

    @staticmethod
    def add_result(interface_name, result):
        """
        Adds the netperf `result` to the shared `netperf_results`

        :param interface_name: interface id of the flow
        :type interface_name: string
        :param result: parsed netperf stats
        :type result: dict
        """
        NetperfResults.netperf_results[interface_name] = result

    @staticmethod
    def output_to_file():
        """
        Outputs the aggregated netperf stats to file
        """
        json_stats = json.dumps(NetperfResults.netperf_results.copy(), indent=4)
        timestamp = time.strftime("%d-%m-%Y-%H:%M:%S")
        filename = str(timestamp) + ' netperf-parse-results.json'
        with open(filename, 'w') as f:
            f.write(json_stats)