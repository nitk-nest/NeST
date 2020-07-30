# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Script to be run for running experiments on topology"""

from multiprocessing import Process

from ..topology_map import TopologyMap
from .. import engine
# Import results
from .results import SsResults, NetperfResults, TcResults, PingResults
# Import parsers
from .parser.ss import SsRunner
from .parser.netperf import NetperfRunner
from .parser.tc import TcRunner
from .parser.ping import PingRunner
# Import plotters
from .plotter.ss import plot_ss
from .plotter.netperf import plot_netperf
from .plotter.tc import plot_tc
from .plotter.ping import plot_ping
from ..experiment.parser.iperf import IperfRunner
from ..engine.util import is_dependency_installed


#pylint: disable=too-many-locals
#pylint: disable=too-many-branches
#pylint: disable=too-many-statements
def run_experiment(exp):
    """
    Run experiment

    Parameters
    -----------
    exp : Experiment
        The experiment attributes
    """

    workers = []
    tc_runners = []
    ss_runners = []
    netperf_runners = []
    iperf_runners = []
    ping_runners = []
    flows = exp.flows

    ss_run = {}
    ping_run = {}

    exp_start = float('inf')
    exp_end = float('-inf')

    dependencies = {}
    for dependency in ['netperf', 'ss', 'tc', 'iperf3', 'ping']:
        dependencies[dependency] = int(is_dependency_installed(dependency))

    # Setup netperf flows and parsing
    for flow in flows:
        # Get flow attributes
        [src_ns, dst_ns, dst_addr, start_t, stop_t,
         n_flows, options] = flow._get_props()  # pylint: disable=protected-access

        exp_start = min(exp_start, start_t)
        exp_end = max(exp_end, stop_t)
        src_name = TopologyMap.get_namespace(src_ns)['name']

        if (src_ns, dst_addr) not in ping_run:
            ping_run[(src_ns, dst_addr)] = (start_t, stop_t)
        else:
            (min_start, max_stop) = ping_run[(src_ns, dst_addr)]
            ping_run[(src_ns, dst_addr)] = (
                min(min_start, start_t), max(max_stop, stop_t))

        if options['protocol'] == 'TCP':
            if dependencies['netperf'] == 0:
                print('Warning: Netperf not found. Tcp flows cannot be generated')
                # To avoid duplicate warning messages
                dependencies['netperf'] = 2
            elif dependencies['netperf'] == 1:
                netperf_options = {}
                NetperfRunner.run_netserver(dst_ns)
                netperf_options['testname'] = 'TCP_STREAM'
                netperf_options['cong_algo'] = options['cong_algo']
                print('Running {} netperf flows from {} to {}...'.format(
                    n_flows, src_name, dst_addr))

                # Create new processes to be run simultaneously
                for _ in range(n_flows):
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
        elif options['protocol'] == 'UDP':
            if dependencies['iperf3'] == 0:
                print('Warning: Iperf3 not found. Udp flows cannot be generated')
                dependencies['iperf3'] = 2      # To avoid duplicate warning messages
            elif dependencies['iperf3'] == 1:
                IperfRunner(dst_ns).run_server()
                print('Running {} udp flows from {} to {}...'.format(
                    n_flows, src_name, dst_addr))
                iperf_runners.append(IperfRunner(src_ns))
                workers.append(
                    Process(target=iperf_runners[-1].run_client,
                            args=[dst_addr, start_t, stop_t-start_t, n_flows, options['target_bw']])
                )

    # Setup ss parsing
    if dependencies['netperf'] == 1:
        if dependencies['ss'] == 1:
            print('Running ss on nodes...')
            print()
            for ns_id, timings in ss_run.items():
                ss_runners.append(SsRunner(ns_id[0], ns_id[1], timings[0],
                                           timings[1] - timings[0]))
                workers.append(Process(target=ss_runners[-1].run))
        else:
            print('Warning: ss not found. Sockets stats will not be collected')

    # Setup tc parsing
    if dependencies['netperf'] == 1:
        if dependencies['tc'] == 1 and len(exp.qdisc_stats) > 0:
            print('Running tc on requested interfaces...')
            print()
            for qdisc_stat in exp.qdisc_stats:
                tc_runners.append(
                    TcRunner(qdisc_stat['ns_id'], qdisc_stat['int_id'], exp_end))
                workers.append(Process(target=tc_runners[-1].run))
        elif dependencies['tc'] != 1:
            print('Warning: tc not found. Qdisc stats will not be collected')

    # Setup ping parsing
    if dependencies['ping'] == 1:
        for ns_id, timings in ping_run.items():
            ping_runners.append(PingRunner(
                ns_id[0], ns_id[1], timings[0], timings[1]-timings[0]))
            workers.append(Process(target=ping_runners[-1].run))
    else:
        print('Warning: ping not found')

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

    for ping_runner in ping_runners:
        runners.append(Process(target=ping_runner.parse))

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
    PingResults.output_to_file()

    print('Plotting results...')

    # Plot results and dump them as images
    workers = []

    workers.append(Process(target=plot_ss, args=(SsResults.get_results(),)))
    workers.append(Process(target=plot_netperf,
                           args=(NetperfResults.get_results(),)))
    workers.append(Process(target=plot_tc, args=(TcResults.get_results(),)))
    workers.append(
        Process(target=plot_ping, args=(PingResults.get_results(),)))

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
    PingResults.remove_all_results()

    # Kill any running processes in namespaces
    for namespace in TopologyMap.get_namespaces():
        engine.kill_all_processes(namespace['id'])
