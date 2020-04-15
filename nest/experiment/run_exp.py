# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# Script to be run for running experiments on the namespaces
# with the json file configurations as command line arguments

import json
from multiprocessing import Process, Lock
import time

from .parser.ss import parse_ss
from .parser.netperf import run_netperf, run_netserver
from ..topology_map import TopologyMap
from .results import SsResults, NetperfResults
from .. import engine
from .plotter.ss import plot_ss

def parse_config(exp):
    """
    Retrieves the experiment object and calls the parsing function

    :param exp: The experiment attributes
    :type exp: Experiment
    """

    workers = []
    flows = exp.get_flows()

    ss_run = {}
    ss_lock = Lock()
    netperf_lock = Lock()
    
    for flow in flows:
        [src_ns, dst_ns, dst_addr, start_t, stop_t, n_flows, cong_alg] = flow._get_props()
        run_netserver(dst_ns)
        # create new processes to be run simultaneously
        # here Process is used instead of Thread to take advantage to multiple cores
        for i in range(n_flows):
            workers.append(Process(target=run_netperf, args=(src_ns, dst_addr, start_t, netperf_lock, cong_alg, stop_t-start_t)))
        
        # Find the start time and stop time to run ss command in `src_ns` to a `dst_addr`
        if (src_ns, dst_addr) not in ss_run:
            ss_run[(src_ns, dst_addr)] = (start_t, stop_t)
        else:
            (min_start, max_stop) = ss_run[(src_ns, dst_addr)]
            ss_run[(src_ns, dst_addr)] = (min(min_start, start_t), max(max_stop, stop_t))

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

    # Dump plots as images
    plot_ss(exp.get_name(), SsResults.get_results())    

    ### Cleanup ###
    # TODO: Make cleanup more explicit rather than
    # as part of parse_config?

    # Remove results of the experiment
    SsResults.remove_all_results()
    NetperfResults.remove_all_results()

    # Kill any running processes in namespaces
    for namespace in TopologyMap.get_namespaces():
        engine.kill_all_processes(namespace['id'])

# NOTE: The below function is no longer supported
# It's a headache to get this and 'test' parsing option
# working. 
# Later on if there is a need, this function will be 
# implemented.
def _parse_config_files(config_files):
    """
    Parses the config files to run tests accordingly 
    """

    raise NotImplementedError('Parsing config file is currently \
            unsupported.')    

    # Loop through all the config files, convert each config file to
    # a dict and run netserver or/and netperf depending on the type of
    # host.
    # TODO: parallelize this so that all the config files can be run simultaneously
    # for config_file in config_files:
        # with open(config_file, 'r') as f:
            # config = json.load(f)
            # _parse_config_from_dict(config)

    
