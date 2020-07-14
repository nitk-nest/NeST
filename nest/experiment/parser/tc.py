# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import re
import json
import subprocess
import shlex
import tempfile
import os
from packaging import version
from nest import engine
from ..results import TcResults
from ...topology_map import TopologyMap


class TcRunner:
    """Runs tc command and stores and parses the output

    Attributes
    ----------
    iterator : str
        absolute path of the tc iterator script
    old_kernel_version : str
        minimum kernel version required
    new_kernel_version : str
        kernel version from which tc has concrete json support
    out : File
        temporary file to hold the stats
    ns_name : str
        network namespace to run tc from
    dev : str
        dev id to collect tc stats from
    run_time : num
        total time to run tc for
    """

    iterator = os.path.realpath(os.path.dirname(__file__)) + "/iterators/tc.sh"
    old_kernel_version = '4.15.0'
    new_kernel_version = '5.5'

    def __init__(self, ns_name, dev, run_time):
        """Constructor to initialize tc runner

        Parameters
        ----------
        ns_name : str
            network namespace to run tc from
        dev : str
            dev id to collect tc stats from
        run_time : num
            total time to run tc for
        """
        self.out = tempfile.TemporaryFile()
        self.ns_name = ns_name
        self.dev = dev
        self.run_time = run_time

    def run(self):
        """runs the tc iterator
        """
        command = "ip netns exec {ns_name} /bin/bash {iterator} {dev} {duration}".format(
            ns_name=self.ns_name, iterator=TcRunner.iterator, dev=self.dev, duration=self.run_time)

        proc = subprocess.Popen(shlex.split(command),
                                stdout=self.out, stderr=subprocess.PIPE)

        proc.communicate()

    def get_qdisc_specific_params(self):
        """parameters to be obtained for a specific qdisc

        Returns
        -------
        dict:
            qdisc keyed list of paramters to parsed
        """
        qdisc_param = {
            'codel': ['count', 'lastcount', 'ldelay', 'drop_next'],
            'fq_codel': ['maxpacket',
                         'drop_overlimit', 'new_flow_count'],
            'pie': ['prob', 'delay', 'avg_dq_rate']
        }
        return qdisc_param

    def get_qdisc_re(self):
        """Compile regular expression for parsing qdisc specific paramters

        Returns
        -------
        dict
            qdisc keyed regular expression
        """
        qdisc_re = {}
        qdisc_re['codel'] = re.compile(r'count (?P<count>\d+) '
                                       r'lastcount (?P<lastcount>\d+) '
                                       r'ldelay (?P<ldelay>[0-9\.]+[mu]?s) '
                                       r"(?P<dropping>dropping)? ?"
                                       r'drop_next (?P<drop_next>-?[0-9\.]+[mu]?s)')
        qdisc_re['fq_codel'] = re.compile(r'maxpacket (?P<maxpacket>\d+) '
                                          r'drop_overlimit (?P<drop_overlimit>\d+) '
                                          r'new_flow_count (?P<new_flow_count>\d+) ')
        qdisc_re['pie'] = re.compile(r'prob (?P<prob>[0-9\.]+) '
                                     r'delay (?P<delay>[0-9\.]+[mu]?s) '
                                     r'avg_dq_rate (?P<avg_dq_rate>\d+)')
        return qdisc_re

    def repl(self, match):
        """Called by re.sub() for every match

        Parameters
        ----------
        match : Match
            Match object captured by the pattern

        Returns
        -------
        str
            string to replace the matched string
        """
        if match.group(1):
            if match.group(1).endswith(','):
                s = repr(match.group(1))
                return ':"{}",'.format(s)
            else:
                s = repr(match.group(1))
                return ':"{}"'.format(s)

    def clean_json(self, stats):
        """json formatted tc stats with invalid json keys
        and values are removed or fixed

        Parameters
        ----------
        stats : str
            unclean json formatted stats

        Returns
        -------
        str
            fixed json stats
        """
        # pattern to remove the options key
        options_pattern = r'"options": {(.|\n)*?},'
        stats = re.sub(options_pattern, '', stats)

        # pattern to enclose all the values with " "
        value_pattern = r':(\s(\w|\s|\n|\.)+,?)'
        stats = re.sub(value_pattern, self.repl, stats)
        return stats

    def old_kernel_version_parse_helper(self, raw_stats, qdisc_param, qdisc_re):
        """Parsing tc command on linux kernel versions
        4.15.0 to 5.4

        Parameters
        ----------
        raw_stats : list(str)
            list of stats collected at each iteration
        qdisc_param : dict
            parameters to be obtained for a specific qdisc
        qdisc_re : dict
            regular expression for parsing qdisc specific paramters

        Returns
        -------
        dict
            handle keyed dict with list of stats
        """

        aggregate_stats = {}

        for raw_stat in raw_stats[:-1]:
            timestamp_pattern = r'timestamp:(?P<timestamp>\d+\.\d+)'
            timestamp = re.search(
                timestamp_pattern, raw_stat).group("timestamp")
            raw_stat = re.sub(timestamp_pattern, "", raw_stat)
            raw_stat = json.loads(self.clean_json(raw_stat))
            stats_dict = {}
            for qdisc_stat in raw_stat:
                qdisc = qdisc_stat['kind']
                if(qdisc in ['codel', 'fq_codel', 'pie']):
                    handle = qdisc_stat['handle']
                    if handle not in aggregate_stats:
                        aggregate_stats[handle] = []
                    qdisc_stat = qdisc_stat['qlen']
                    search_obj = qdisc_re[qdisc].search(qdisc_stat)
                    stats_dict['timestamp'] = str(timestamp)
                    stats_dict['kind'] = qdisc
                    for param in qdisc_param[qdisc]:
                        stats_dict[param] = search_obj.group(param)
                    aggregate_stats[handle].append(stats_dict)
        return aggregate_stats

    def new_kernel_version_parse_helper(self, raw_stats):
        """
        Parsing tc command on linux kernel version
        5.5 and above

        Parameters
        ----------
        raw_stats : list(str)
            list of stats collected at each iteration

        Returns
        -------
        dict
            handle keyed dict with list of stats
        """
        aggregate_stats = {}
        for raw_stat in raw_stats[-1]:
            raw_stat = json.loads(self.clean_json(raw_stat))
            stats_dict = {}
            timestamp_pattern = r'timestamp:(?P<timestamp>\d+\.\d+)'
            timestamp = re.search(
                timestamp_pattern, raw_stat).group("timestamp")
            for qdisc_stat in raw_stat:
                qdisc = qdisc_stat['kind']
                if qdisc in ['codel', 'fq_codel', 'pie']:
                    handle = qdisc_stat['handle']
                    if handle not in aggregate_stats:
                        aggregate_stats[handle] = []

                    stats_dict['timestamp'] = str(timestamp)
                    stats_dict.update(qdisc_stat)
                    stats_dict.pop('handle', None)
                    stats_dict.pop('options', None)
                    stats_dict.pop('parent', None)

                    aggregate_stats[handle].append(stats_dict)
        return aggregate_stats

    def parse(self):
        """parses the required data from tc-qdisc output
        """

        self.out.seek(0)    # rewind to start of the temp file

        # See `iterators/tc.sh` for output format
        raw_stats = self.out.read().decode().split("---")

        qdisc_param = self.get_qdisc_specific_params()
        qdisc_re = self.get_qdisc_re()
        aggregate_stats = {}

        # tc produces different JSON ouput format
        # based on the kernel version
        kernel_version = engine.get_kernel_version()
        if version.parse(kernel_version) >= version.parse(TcRunner.new_kernel_version):
            aggregate_stats = self.new_kernel_version_parse_helper(raw_stats)
        elif version.parse(kernel_version) >= version.parse(TcRunner.old_kernel_version):
            aggregate_stats = self.old_kernel_version_parse_helper(raw_stats,
                                                                   qdisc_param, qdisc_re)
        else:
            # TODO: Not sure if it's the right exception to raise
            raise SystemError(
                'NeST does not support tc parsing for kernel version below {}'.format(TcRunner.old_kernel_version))

        # Store parsed results
        dev_name = TopologyMap.get_interface(self.ns_name, self.dev)['name']
        TcResults.add_result(self.ns_name, {dev_name: aggregate_stats})
