# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import re
import json
import subprocess
import time
import numpy as np
from packaging import version
from ..results import TcResults
from nest import engine
from nest.topology_map import TopologyMap

INTERVAL = 0.2
RUN_TIME = 10
STATS_TO_PLOT = list()

def get_qdisc_specific_params():
    """
    parameters to be obtained for a specific qdisc
    :returns dict
    """
    qdisc_param = {}
    qdisc_param['codel'] = ['count', 'lastcount', 'ldelay', 'drop_next']
    qdisc_param['fq_codel'] = ['maxpacket', 'drop_overlimit', 'new_flow_count']
    qdisc_param['pie'] = ['prob', 'delay', 'avg_dq_rate']
    return qdisc_param

def get_qdisc_re():
    """
    Compile regular expression for parsing qdisc specific paramters
    :returns dict
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


def run_tc(cmd):
    """
    runs the tc command

    :param cmd: conmplete tc command to be run
    :type cmd: string

    :return output of the tc command
    """
    proc = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = proc.communicate()

    # if there is an error
    if stderr:
        return None

    return stdout.decode()  # stdout is a bytes-like object. Hence the usage of decode()

def repl(match):
    """
    called be re.sub() for every match
    :returns string
    """
    if match.group(1):
        if match.group(1).endswith(','):
            s = repr(match.group(1))
            return ':"{}",'.format(s)
        else:
            s = repr(match.group(1))
            return ':"{}"'.format(s)

def clean_json(stats):
    """
    json formatted tc stats with invalid json keys
    and values are removed or fixed

    :returns string
    """
    #pattern to remove the options key
    options_pattern = r'"options": {(.|\n)*?},'
    stats = re.sub(options_pattern, '', stats)

    #pattern to enclose all the values with " "
    value_pattern = r':(\s(\w|\s|\n|\.)+,?)'
    stats = re.sub(value_pattern, repl, stats)
    return stats

def old_kernel_version_parse_helper(command, start_time, qdisc_param, qdisc_re, aggregate_stats):
    """
    Parsing tc command on linux kernel versions
    4.15.0 to 5.4
    """
    
    # This loop runs the tc command every `INTERVAL`s for `RUN_TIME`s
    while time.time() <= (start_time+RUN_TIME):
        stats = run_tc(command)
        stats = json.loads(clean_json(stats))
        stats_dict = {}
        cur_timestamp = time.time()
        for qdisc_stat in stats:
            qdisc = qdisc_stat['kind']
            if(qdisc in ['codel', 'fq_codel', 'pie']):
                handle = qdisc_stat['handle']
                if handle not in aggregate_stats:
                    aggregate_stats[handle] = []
                qdisc_stat = qdisc_stat['qlen']
                search_obj = qdisc_re[qdisc].search(qdisc_stat)
                stats_dict['timestamp'] = str(cur_timestamp)
                stats_dict['kind'] = qdisc
                for param in qdisc_param[qdisc]:
                    stats_dict[param] = search_obj.group(param)
                aggregate_stats[handle].append(stats_dict)

        time.sleep(INTERVAL)

def new_kernel_version_parse_helper(command, start_time, qdisc_param, qdisc_re, aggregate_stats):
    """
    Parsing tc command on linux kernel version
    5.5 and above
    """
    
    # This loop runs the tc command every `INTERVAL`s for `RUN_TIME`s
    while time.time() <= (start_time+RUN_TIME):
        stats = run_tc(command)
        stats = json.loads(clean_json(stats))
        # print(json.dumps(stats, indent=4))
        stats_dict = {}
        cur_timestamp = time.time()
        for qdisc_stat in stats:
            qdisc = qdisc_stat['kind']
            if qdisc in ['codel', 'fq_codel', 'pie']:
                handle = qdisc_stat['handle']
                if handle not in aggregate_stats:
                    aggregate_stats[handle] = []

                stats_dict['timestamp'] = str(cur_timestamp)
                stats_dict.update(qdisc_stat)
                stats_dict.pop('handle', None)
                stats_dict.pop('options', None)
                stats_dict.pop('parent', None)

                aggregate_stats[handle].append(stats_dict)

        time.sleep(INTERVAL)

def parse(ns_name, dev, stats_to_plot):
    """

    parses the required data from tc-qdisc output

    :param ns_name: namespace name of the router
    :type ns_name: string
    :param dev: interface id 
    :type dev: string
    """

    command = 'ip netns exec {} tc -s -j qdisc show dev {}'.format(ns_name, dev)
    start_time = time.time()
    qdisc_param = get_qdisc_specific_params()
    qdisc_re = get_qdisc_re()
    aggregate_stats = {}

    # tc produces different JSON ouput format
    # based on the kernel version
    kernel_version = engine.get_kernel_version()
    if version.parse(kernel_version) >= version.parse('5.5'):
        new_kernel_version_parse_helper(command, start_time, qdisc_param, qdisc_re, aggregate_stats)
    elif version.parse(kernel_version) >= version.parse('4.15.0'):
        old_kernel_version_parse_helper(command, start_time, qdisc_param, qdisc_re, aggregate_stats)
    else:
        # TODO: Not sure if it's the right exception to raise
        raise SystemError('NeST does not support tc parsing for kernel version below 4.15.0')

    # Store parsed results
    dev_name = TopologyMap.get_interface(ns_name, dev)['name']
    TcResults.add_result(ns_name, {dev_name : aggregate_stats})
    
def parse_qdisc(ns_name, dev, stats_to_plot, run_time):
    """
    runs the tc parser

    :param ns_name: namespace name
    :type ns_name: string
    :param dev: interface id
    :type dev: string
    :param run_time: duration to parse the tc stats
    :type run_time: string 
    """
    global RUN_TIME
    RUN_TIME = run_time
    global STATS_TO_PLOT
    STATS_TO_PLOT = stats_to_plot
    parse(ns_name, dev, [])
