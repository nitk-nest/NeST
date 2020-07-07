# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import json
import time
from multiprocessing import Manager, Lock, Queue
from ..topology_map import TopologyMap
from .pack import Pack


class Results:
    """
    This class aggregates the stats from the entire experiment environment
    """
    @staticmethod
    def add_result(results_q, ns_id, result):
        """
        Adds the stats parse from a process to the shared `results_q`
        
        :param results_q: Shared stats
        :type results_q: multiprocessing.Manager.Queue
        :param ns_id: namespace id (internal name)
        :type ns_id: string
        :param result: parsed stats
        :type result: dict
        """

        # Convert nest's internal name to user given name
        ns_name = TopologyMap.get_namespace(ns_id)['name']

        item = results_q.get()
        if ns_name not in item:
            item[ns_name] = [result]
        else:
            temp = item[ns_name]
            temp.append(result)
            item[ns_name] = temp
        results_q.put(item)

    @staticmethod
    def remove_all_results(results_q):
        """
        Remove all results obtained from the experiment

        :param results_q: Shared stats
        :type results_q: multiprocessing.Manager.Queue
        """

        results_q.get()
        results_q.put({})

    @staticmethod
    def get_results(results_q):
        """
        Get results obtained in the experiment so far

        :param results_q: Shared stats
        :type results_q: multiprocessing.Manager.Queue
        """

        results = results_q.get()
        results_q.put(results)
        return results

    @staticmethod
    def output_to_file(results_q, toolname):
        """
        Outputs the aggregated ss stats to file

        :param results_q: Shared stats
        :type results_q: multiprocessing.Manager.Queue
        """

        results = Results.get_results(results_q)
        json_stats = json.dumps(results, indent=4)
        Pack.dump_file('{}.json'.format(toolname), json_stats)


# Shared variables to aggregate results
ss_results_q = Manager().Queue()
ss_results_q.put({})


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

        Results.add_result(ss_results_q, ns_id, result)

    @staticmethod
    def remove_all_results():
        """
        Remove all results obtained from the experiment
        """

        Results.remove_all_results(ss_results_q)

    @staticmethod
    def get_results():
        """
        Get results obtained in the experiment so far
        """

        return Results.get_results(ss_results_q)

    @staticmethod
    def output_to_file():
        """
        Outputs the aggregated ss stats to file
        """

        Results.output_to_file(ss_results_q, 'ss')


# Shared variables to aggregate results
netperf_results_q = Manager().Queue()
netperf_results_q.put({})


class NetperfResults:
    """
    This class aggregates the netperf stats from the entire experiment environment
    """
    @staticmethod
    def add_result(ns_id, result):
        """
        Adds the netperf stats parse from a process to the shared `netperf_results`

        :param ns_id: namespace id (internal name)
        :type ns_id: string
        :param result: parsed netperf stats
        :type result: dict
        """

        Results.add_result(netperf_results_q, ns_id, result)

    @staticmethod
    def remove_all_results():
        """
        Remove all results obtained from the experiment
        """

        Results.remove_all_results(netperf_results_q)

    @staticmethod
    def get_results():
        """
        Get results obtained in the experiment so far
        """

        return Results.get_results(netperf_results_q)

    @staticmethod
    def output_to_file():
        """
        Outputs the aggregated netperf stats to file
        """

        Results.output_to_file(netperf_results_q, 'netperf')


# Shared variables to aggregate results
tc_results_q = Manager().Queue()
tc_results_q.put({})


class TcResults:
    """
    This class aggregates the tc stats from the entire experiment environment
    """
    @staticmethod
    def add_result(ns_id, result):
        """
        Adds the tc stats parse from a process to the shared `tc_results`

        :param ns_id: namespace id (internal name)
        :type ns_id: string
        :param result: parsed tc stats
        :type result: dict
        """

        Results.add_result(tc_results_q, ns_id, result)

    @staticmethod
    def remove_all_results():
        """
        Remove all results obtained from the experiment
        """

        Results.remove_all_results(tc_results_q)

    @staticmethod
    def get_results():
        """
        Get results obtained in the experiment so far
        """

        return Results.get_results(tc_results_q)

    @staticmethod
    def output_to_file():
        """
        Outputs the aggregated tc stats to file
        """

        Results.output_to_file(tc_results_q, 'tc')
