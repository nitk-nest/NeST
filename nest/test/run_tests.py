# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# Script to be run for running tests on the namespaces
# with the json file configurations as command line arguments

import json
from multiprocessing import Process, Lock
import time

from .ss_parse import parse_ss
from .tc_parse import parse_qdisc
from .netperf import run_netperf, run_netserver
from ..configuration import Configuration
from .results import SsResults, NetperfResults

def fetch_host_stats(ns_name, config):
    parse_ss(ns_name, config['destination'], config['stats_to_plot'] , 2)


def fetch_router_stats(ns_name, config):
    parse_qdisc(ns_name, config['stats_to_plot'], 2)
    pass


def parse_config():
    """
    retreives the config dict and calls the parsing function
    """

    config = Configuration.get_config()
    _parse_config_from_dict(config)


def _parse_config_files(config_files):
    """
    Parses the config files to run tests accordingly 
    """

    # Loop through all the config files, convert each config file to
    # a dict and run netserver or/and netperf depending on the type of
    # host.
    # TODO: parallelize this so that all the config files can be run simultaneously
    for config_file in config_files:
        with open(config_file, 'r') as f:
            config = json.load(f)
            _parse_config_from_dict(config)


def _parse_config_from_dict(config):
    """
    Parses the `config` to run tests accordingly
    """
    workers = []
    tests = config['tests']

    ss_run = {}
    ss_lock = Lock()
    netperf_lock = Lock()
    
    for test in tests:
        run_netserver(test['dst_ns'])
        # create new processes to be run simultaneously
        # here Process is used instead of Thread to take advantage to multiple cores
        for i in range(test['n_flows']):
            workers.append(Process(target=run_netperf, args=(test['src_ns'], test['dst_addr'], test['start_t'], netperf_lock, test['stop_t']-test['start_t'])))
        # workers.append(Process(target=parse_ss, args=(test['src_ns'], test['dst_addr'], [], test['start_t'], test['stop_t'] - test['start_t'])))
        
        # Find the start time and stop time to run ss command in `src_ns` to a `dst_addr`
        if (test['src_ns'], test['dst_addr']) not in ss_run:
            ss_run[(test['src_ns'], test['dst_addr'])] = (test['start_t'], test['stop_t'])
        else:
            (min_start, max_stop) = ss_run[(test['src_ns'], test['dst_addr'])]
            ss_run[(test['src_ns'], test['dst_addr'])] = (min(min_start, test['start_t']), max(max_stop, test['stop_t']))

    for key, value in ss_run.items():
        workers.append(Process(target=parse_ss, args=(key[0], key[1], [], value[0], value[1] - value[0], ss_lock)))

    # start all the processes
    for worker in workers:
        worker.start()

    # wait for all the processes to finish
    for worker in workers:
        worker.join()

    SsResults.output_to_file()
    NetperfResults.output_to_file()
    

