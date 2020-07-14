# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# Script to be run for running experiments on the namespaces

from multiprocessing import Process

from ..topology_map import TopologyMap
from .. import engine
# Import results
from .results import SsResults, NetperfResults, TcResults
# Import parsers
from .parser.ss import SsRunner
from .parser.netperf import NetperfRunner
from .parser.tc import TcRunner
# Import plotters
from .plotter.ss import plot_ss
from .plotter.netperf import plot_netperf
from .plotter.tc import plot_tc


def run_experiment(exp):
    """
    Run experiment

    :param exp: The experiment attributes
    :type exp: Experiment
    """

    workers = []
    tc_runners = []
    ss_runners = []
    netperf_runners = []
    flows = exp.get_flows()

    ss_run = {}
    
    exp_start = float('inf')
    exp_end = float('-inf')

    # Setup netperf flows and parsing
    for flow in flows:
        # Get flow attributes
        [src_ns, dst_ns, dst_addr, start_t, stop_t,
            n_flows, options] = flow._get_props()

        exp_start = min(exp_start, start_t)
        exp_end = max(exp_end, stop_t)

        NetperfRunner.run_netserver(dst_ns)

        netperf_options = {}
        if options['protocol'] == 'TCP':
            netperf_options['testname'] = 'TCP_STREAM'
            netperf_options['cong_algo'] = options['cong_algo']
        elif options['protocol'] == 'UDP':
            netperf_options['testname'] = 'UDP_STREAM'

        src_name = TopologyMap.get_namespace(src_ns)['name']
        print('Running {} netperf flows from {} to {}...'.format(
            n_flows, src_name, dst_addr))

        # Create new processes to be run simultaneously
        for i in range(n_flows):
            netperf_runners.append(NetperfRunner(
                src_ns, dst_addr, start_t, stop_t-start_t, **netperf_options))
            workers.append(Process(target=netperf_runners[-1].run))

        # Find the start time and stop time to run ss command in `src_ns` to a `dst_addr`
        if (src_ns, dst_addr) not in ss_run:
            ss_run[(src_ns, dst_addr)] = (start_t, stop_t)
        else:
            (min_start, max_stop) = ss_run[(src_ns, dst_addr)]
            ss_run[(src_ns, dst_addr)] = (
                min(min_start, start_t), max(max_stop, stop_t))

    print('Running ss and tc on requested nodes and interfaces...')
    print()

    # Setup ss parsing
    for key, value in ss_run.items():
        ss_runners.append(SsRunner(key[0], key[1], value[0],
                                   value[1] - value[0]))
        workers.append(Process(target=ss_runners[-1].run))

    # Setup tc parsing
    for qdisc_stat in exp.qdisc_stats:
        tc_runners.append(
            TcRunner(qdisc_stat['ns_id'], qdisc_stat['int_id'], exp_end))
        workers.append(Process(target=tc_runners[-1].run))

    # Start parsing (start all processes)
    for worker in workers:
        worker.start()

    # wait for all the processes to finish
    for worker in workers:
        worker.join()

    print('Experiment complete!')
    print("Parsing statistics...")

    runners = []
    for ss_runner in ss_runners:
        runners.append(Process(target=ss_runner.parse))

    for netperf_runner in netperf_runners:
        runners.append(Process(target=netperf_runner.parse))

    for tc_runner in tc_runners:
        runners.append(Process(target=tc_runner.parse))

    # iterate thourough the runners and parse the stored statistics
    for runner in runners:
        runner.start()

    # wait for the runners to finish
    for runner in runners:
        runner.join()

    print('Output results as JSON dump')

    # Output results as JSON dumps
    SsResults.output_to_file()
    NetperfResults.output_to_file()
    TcResults.output_to_file()

    print('Plotting results...')

    # Plot results and dump them as images
    workers = []

    workers.append(Process(target=plot_ss, args=(
        exp.get_name(), SsResults.get_results())))
    workers.append(Process(target=plot_netperf, args=(
        exp.get_name(), NetperfResults.get_results())))
    workers.append(Process(target=plot_tc, args=(
        exp.get_name(), TcResults.get_results())))

    # Start plotting
    for worker in workers:
        worker.start()

    # Wait for all processes to finish
    for worker in workers:
        worker.join()

    print('Plotting complete!')

    ### Cleanup ###

    # Remove results of the experiment
    SsResults.remove_all_results()
    NetperfResults.remove_all_results()
    TcResults.remove_all_results()

    # Kill any running processes in namespaces
    for namespace in TopologyMap.get_namespaces():
        engine.kill_all_processes(namespace['id'])

    print('Cleaned up experiment')

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
