# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import json
import time
from multiprocessing import Manager, Lock, Queue
from ..topology_map import TopologyMap

# Shared variables to aggregate results
ss_results_q = Manager().Queue()
ss_results_q.put({})

netperf_results_q = Manager().Queue()
netperf_results_q.put({})

class SsResults:
    """
    This class aggregates the ss stats from the entire experiment environment
    """
    @staticmethod
    def add_result(ns_id, result):
        """
        Adds the ss stats parse from a process to the shared `ss_results`
        :param ns_id: namespace id (internal name)
        :type ns_id: string
        :param result: parsed ss stats
        :type result: dict
        """

        # Convert nest's internal name to user given name
        ns_name = TopologyMap.get_namespace(ns_id)['name']

        item = ss_results_q.get()
        if ns_name not in item:
            item[ns_name] = [result]
        else:
            temp = item[ns_name]
            temp.append(result)
            item[ns_name] = temp
        ss_results_q.put(item)

    @staticmethod
    def remove_all_results():
        """
        Remove all results obtained from the experiment
        """

        ss_results_q.get()
        ss_results_q.put({})
    
    @staticmethod
    def get_results():
        """
        Get results obtained in the experiment so far
        """

        ss_results = ss_results_q.get()
        ss_results_q.put(ss_results)
        return ss_results

    @staticmethod
    def output_to_file():
        """
        Outputs the aggregated ss stats to file
        """

        ss_results = SsResults.get_results()
        json_stats = json.dumps(ss_results, indent=4)
        timestamp = time.strftime("%d-%m-%Y-%H:%M:%S")
        filename = str(timestamp) + ' ss-parse-results.json'
        with open(filename, 'w') as f:
            f.write(json_stats)

class NetperfResults:
    """
    This class aggregates the netperf stats from the entire experiment environment
    """
    @staticmethod
    def add_result(ns_id, result):
        """
        Adds the netperf `result` to the shared `netperf_results`

        :param ns_id: namespace id of the flow (Nest's internal name)
        :type ns_id: string
        :param result: parsed netperf stats
        :type result: dict
        """

        # Convert nest's internal name to user given name
        ns_name = TopologyMap.get_namespace(ns_id)['name']

        item = netperf_results_q.get()
        if ns_name not in item:
            item[ns_name] = [result]
        else:
            temp = item[ns_name]
            temp.append(result)
            item[ns_name] = temp

        netperf_results_q.put(item)

    @staticmethod
    def remove_all_results():
        """
        Remove all results obtained from the experiment
        """ 

        netperf_results_q.get()
        netperf_results_q.put({})

    @staticmethod
    def get_results():
        """
        Get results obtained in the experiment so far
        """

        netperf_results = netperf_results_q.get()
        netperf_results_q.put(netperf_results)
        return netperf_results

    @staticmethod
    def output_to_file():
        """
        Outputs the aggregated netperf stats to file
        """

        netperf_results = NetperfResults.get_results()
        json_stats = json.dumps(netperf_results, indent=4)
        timestamp = time.strftime("%d-%m-%Y-%H:%M:%S")
        filename = str(timestamp) + ' netperf-parse-results.json'
        with open(filename, 'w') as f:
            f.write(json_stats)