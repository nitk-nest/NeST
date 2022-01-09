# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Handles collection of results (raw data)"""

import json
from multiprocessing import Manager
from ..topology_map import TopologyMap
from .pack import Pack


class Results:
    """This class aggregates the stats from the entire experiment environment"""

    @staticmethod
    def add_result(results_q, ns_id, result):
        """
        Adds the stats parse from a process to the shared `results_q`

        Parameters
        ----------
        results_q : multiprocessing.Manager.Queue
            Shared stats
        ns_id : string
            namespace id (internal name)
        result : dict
            parsed stats
        """
        # Convert nest's internal name to user given name
        ns_name = TopologyMap.get_namespace(ns_id)["name"]

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

        Parameters
        ----------
        results_q : multiprocessing.Manager.Queue
            Shared stats
        """
        results_q.get()
        results_q.put({})

    @staticmethod
    def get_results(results_q):
        """
        Get results obtained in the experiment so far

        Parameters
        ----------
        results_q : multiprocessing.Manager.Queue
            Shared stats
        """
        results = results_q.get()
        results_q.put(results)
        return results

    @staticmethod
    def output_to_file(results_q, toolname):
        """
        Outputs the aggregated results into a file.
        If results are empty, then it is not output to file.

        Parameters
        ----------
        results_q : multiprocessing.Manager.Queue
            Shared stats
        toolname : str
            Like ss, tc, netperf
        """
        results = Results.get_results(results_q)
        if results:
            json_stats = json.dumps(results, indent=4)
            Pack.dump_file("{}.json".format(toolname), json_stats)


# Shared variables to aggregate results
ss_results_q = Manager().Queue()
ss_results_q.put({})


class SsResults:
    """This class aggregates the ss stats from the entire experiment environment"""

    @staticmethod
    def add_result(ns_id, result):
        """Adds the ss stats parse from a process to the shared `ss_results`

        Parameters
        ----------
        ns_id : string
            namespace id (internal name)
        result : dict
            parsed ss stats
        """
        Results.add_result(ss_results_q, ns_id, result)

    @staticmethod
    def remove_all_results():
        """Remove all results obtained from the experiment"""
        Results.remove_all_results(ss_results_q)

    @staticmethod
    def get_results():
        """Get results obtained in the experiment so far"""
        return Results.get_results(ss_results_q)

    @staticmethod
    def output_to_file():
        """Outputs the aggregated ss stats to file"""
        Results.output_to_file(ss_results_q, "ss")


# Shared variables to aggregate results
netperf_results_q = Manager().Queue()
netperf_results_q.put({})


class NetperfResults:
    """This class aggregates the netperf stats from the entire experiment environment"""

    @staticmethod
    def add_result(ns_id, result):
        """Adds the netperf stats parse from a process to the shared `netperf_results`

        Parameters
        ----------
        ns_id : string
            namespace id (internal name)
        result : dict
            parsed netperf stats
        """
        Results.add_result(netperf_results_q, ns_id, result)

    @staticmethod
    def remove_all_results():
        """Remove all results obtained from the experiment"""
        Results.remove_all_results(netperf_results_q)

    @staticmethod
    def get_results():
        """Get results obtained in the experiment so far"""
        return Results.get_results(netperf_results_q)

    @staticmethod
    def output_to_file():
        """Outputs the aggregated netperf stats to file"""
        Results.output_to_file(netperf_results_q, "netperf")


# Shared variables to aggregate results
iperf3_results_q = Manager().Queue()
iperf3_results_q.put({})


class Iperf3Results:
    """This class aggregates the iperf3 stats from the entire experiment environment"""

    @staticmethod
    def add_result(ns_id, result):
        """Adds the iperf3 stats parsed from a process to the shared `iperf3_results`

        Parameters
        ----------
        ns_id : string
            namespace id (internal name)
        result : dict
            parsed netperf stats
        """
        Results.add_result(iperf3_results_q, ns_id, result)

    @staticmethod
    def remove_all_results():
        """Remove all results obtained from the experiment"""
        Results.remove_all_results(iperf3_results_q)

    @staticmethod
    def get_results():
        """Get results obtained in the experiment so far"""
        return Results.get_results(iperf3_results_q)

    @staticmethod
    def output_to_file():
        """Outputs the aggregated netperf stats to file"""
        Results.output_to_file(iperf3_results_q, "iperf3")


# Shared variables to aggregate results
tc_results_q = Manager().Queue()
tc_results_q.put({})


class TcResults:
    """This class aggregates the tc stats from the entire experiment environment"""

    @staticmethod
    def add_result(ns_id, result):
        """Adds the tc stats parse from a process to the shared `tc_results`

        Parameters
        ----------
        ns_id : string
            namespace id (internal name)
        result : dict
            parsed tc stats
        """
        Results.add_result(tc_results_q, ns_id, result)

    @staticmethod
    def remove_all_results():
        """Remove all results obtained from the experiment"""
        Results.remove_all_results(tc_results_q)

    @staticmethod
    def get_results():
        """Get results obtained in the experiment so far"""
        return Results.get_results(tc_results_q)

    @staticmethod
    def output_to_file():
        """Outputs the aggregated tc stats to file"""
        Results.output_to_file(tc_results_q, "tc")


ping_results_q = Manager().Queue()
ping_results_q.put({})


class PingResults:
    """This class aggregates the ping stats from the entire experiment environment"""

    @staticmethod
    def add_result(ns_id, result):
        """Adds the ping stats parse from a process to the shared `ping_results`

        Parameters
        ----------
        ns_id : string
            namespace id (internal name)
        result : dict
            parsed ping stats
        """
        Results.add_result(ping_results_q, ns_id, result)

    @staticmethod
    def remove_all_results():
        """Remove all results obtained from the experiment"""
        Results.remove_all_results(ping_results_q)

    @staticmethod
    def get_results():
        """Get results obtained in the experiment so far"""
        return Results.get_results(ping_results_q)

    @staticmethod
    def output_to_file():
        """Outputs the aggregated ping stats to file"""
        Results.output_to_file(ping_results_q, "ping")
