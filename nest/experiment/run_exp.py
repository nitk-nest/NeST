# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Script to be run for running experiments on topology"""

from multiprocessing import Process
from collections import namedtuple, defaultdict
import logging
import os
from time import sleep
from tqdm import tqdm

from nest.logging_helper import DepedencyCheckFilter
from nest import config
from nest.topology_map import TopologyMap
from nest.clean_up import kill_processes
from .pack import Pack

# Import results
from .results import SsResults, NetperfResults, Iperf3Results, TcResults, PingResults

# Import parsers
from .parser.ss import SsRunner
from .parser.netperf import NetperfRunner
from .parser.iperf3 import Iperf3Runner
from .parser.tc import TcRunner
from .parser.ping import PingRunner

# Import plotters
from .plotter.ss import plot_ss
from .plotter.netperf import plot_netperf
from .plotter.iperf3 import plot_iperf3
from .plotter.tc import plot_tc
from .plotter.ping import plot_ping
from ..engine.util import is_dependency_installed

logger = logging.getLogger(__name__)
if not any(isinstance(filter, DepedencyCheckFilter) for filter in logger.filters):
    # Duplicate filter is added to avoid logging of same error
    # messages incase any of the tools is not installed
    logger.addFilter(DepedencyCheckFilter())

# pylint: disable=too-many-locals
def run_experiment(exp):
    """
    Run experiment

    Parameters
    -----------
    exp : Experiment
        The experiment attributes
    """

    tools = ["netperf", "ss", "tc", "iperf3", "ping"]
    Runners = namedtuple("runners", tools)
    exp_runners = Runners(
        netperf=[], ss=[], tc=[], iperf3=[], ping=[]
    )  # Runner objects

    # Keep track of all destination nodes [to ensure netperf and iperf3
    # server is run at most once]
    destination_nodes = {"netperf": set(), "iperf3": set()}

    # Contains start time and end time to run respective command
    # from a source netns to destination address (in destination netns)
    ss_schedules = defaultdict(lambda: (float("inf"), float("-inf")))
    ping_schedules = defaultdict(lambda: (float("inf"), float("-inf")))

    # Overall experiment stop time considering all flows
    exp_end_t = float("-inf")

    dependencies = get_dependency_status(tools)

    ss_required = False
    ss_filters = set()

    # Traffic generation
    for flow in exp.flows:
        # Get flow attributes
        [
            src_ns,
            dst_ns,
            dst_addr,
            start_t,
            stop_t,
            _,
            options,
        ] = flow._get_props()  # pylint: disable=protected-access

        exp_end_t = max(exp_end_t, stop_t)

        (min_start, max_stop) = ping_schedules[(src_ns, dst_ns, dst_addr)]
        ping_schedules[(src_ns, dst_ns, dst_addr)] = (
            min(min_start, start_t),
            max(max_stop, stop_t),
        )

        # Setup TCP/UDP flows
        if options["protocol"] == "TCP":
            # * Ignore netperf tcp control connections
            # * Destination port of netperf control connection is 12865
            # * We also have "sport" (source port) in the below condition since
            #   there can be another flow in the reverse direction whose control
            #   connection also we must ignore.
            ss_filters.add("sport != 12865 and dport != 12865")
            ss_required = True
            (tcp_runners, ss_schedules,) = setup_tcp_flows(
                dependencies["netperf"],
                flow,
                ss_schedules,
                destination_nodes["netperf"],
            )

            exp_runners.netperf.extend(tcp_runners)

            # Update destination nodes
            destination_nodes["netperf"].add(dst_ns)

        elif options["protocol"] == "UDP":
            # * Ignore iperf3 tcp control connections
            # * Destination port of iperf3  control connection is 5201
            # * We also have "sport" (source port) in the below condition since
            #   there can be another flow in the reverse direction whose control
            #   connection also we must ignore.
            ss_filters.add("sport != 5201 and dport != 5201")
            udp_runners = setup_udp_flows(
                dependencies["iperf3"], flow, destination_nodes["iperf3"]
            )

            exp_runners.iperf3.extend(udp_runners)

            # Update destination nodes
            destination_nodes["iperf3"].add(dst_ns)

    if ss_required:
        ss_filter = " and ".join(ss_filters)
        ss_runners = setup_ss_runners(dependencies["ss"], ss_schedules, ss_filter)
        exp_runners.ss.extend(ss_runners)

    tc_runners = setup_tc_runners(dependencies["tc"], exp.qdisc_stats, exp_end_t)
    exp_runners.tc.extend(tc_runners)

    ping_runners = setup_ping_runners(dependencies["ping"], ping_schedules)
    exp_runners.ping.extend(ping_runners)

    # Start traffic generation
    run_workers(setup_flow_workers(exp_runners, exp_end_t))

    logger.info("Experiment complete!")
    logger.info("Parsing statistics...")

    # Parse the stored statistics
    run_workers(setup_parser_workers(exp_runners))

    logger.info("Output results as JSON dump")

    # Output results as JSON dumps
    dump_json_ouputs()

    if config.get_value("plot_results"):
        logger.info("Plotting results...")

        # Plot results and dump them as images
        run_workers(setup_plotter_workers())

        logger.info("Plotting complete!")

    if config.get_value("readme_in_stats_folder"):
        # Copying README.txt to stats folder
        relative_path = os.path.join("info", "README.txt")
        readme_path = os.path.join(os.path.dirname(__file__), relative_path)
        Pack.copy_files(readme_path)

    cleanup()


def run_workers(workers):
    """
    Run and wait for processes to finish

    Parameters
    ----------
    workers: list[multiprocessing.Process]
        List of processes to be run
    """
    # Start workers
    for worker in workers:
        worker.start()

    # wait for all the workers to finish
    for worker in workers:
        worker.join()


def setup_plotter_workers():
    """
    Setup plotting processes

    Returns
    -------
    List[multiprocessing.Process]
        plotters
    """
    plotters = []

    plotters.append(Process(target=plot_ss, args=(SsResults.get_results(),)))
    plotters.append(Process(target=plot_netperf, args=(NetperfResults.get_results(),)))
    plotters.append(Process(target=plot_iperf3, args=(Iperf3Results.get_results(),)))
    plotters.append(Process(target=plot_tc, args=(TcResults.get_results(),)))
    plotters.append(Process(target=plot_ping, args=(PingResults.get_results(),)))

    return plotters


def dump_json_ouputs():
    """
    Outputs experiment results as json dumps
    """
    SsResults.output_to_file()
    NetperfResults.output_to_file()
    Iperf3Results.output_to_file()
    TcResults.output_to_file()
    PingResults.output_to_file()


def setup_flow_workers(exp_runners, exp_stop_time):
    """
    Setup flow generation and stats collection processes(netperf, ss, tc, iperf3...).

    Also add a progress bar process for showing experiment progress.

    Parameters
    ----------
    exp_runners: collections.NamedTuple
        all(netperf, ping, ss, tc..) the runners
    exp_stop_time: int
        Time when experiment stops (in seconds)

    Returns
    -------
    List[multiprocessing.Process]
        flow generation and stats collection processes
        + progress bar process
    """
    workers = []

    for runners in exp_runners:
        workers.extend([Process(target=runner.run) for runner in runners])

    # Add progress bar process
    if config.get_value("show_progress_bar"):
        workers.extend([Process(target=progress_bar, args=(exp_stop_time,))])

    return workers


def setup_parser_workers(exp_runners):
    """
    Setup parsing processes

    Parameters
    ----------
    exp_runners: collections.NamedTuple
        all(netperf, ping, ss, tc..) the runners

    Returns
    -------
    List[multiprocessing.Process]
        parsers
    """
    parsers = []

    for ss_runner in exp_runners.ss:
        parsers.append(Process(target=ss_runner.parse))

    for netperf_runner in exp_runners.netperf:
        parsers.append(Process(target=netperf_runner.parse))

    for iperf3_runner in exp_runners.iperf3:
        parsers.append(Process(target=iperf3_runner.parse))

    for tc_runner in exp_runners.tc:
        parsers.append(Process(target=tc_runner.parse))

    for ping_runner in exp_runners.ping:
        parsers.append(Process(target=ping_runner.parse))

    return parsers


def get_dependency_status(tools):
    """
    Checks for dependency

    Parameters
    ----------
    tools: List[str]
        list of tools to check for it's installation

    Returns
    -------
    dict
        contains information as to whether `tools` are installed
    """
    dependencies = {}
    for dependency in tools:
        dependencies[dependency] = is_dependency_installed(dependency)
    return dependencies


def setup_tcp_flows(dependency, flow, ss_schedules, destination_nodes):
    """
    Setup netperf to run tcp flows
    Parameters
    ----------
    dependency: int
        whether netperf is installed
    flow: Flow
        Flow parameters
    ss_schedules:
        ss_schedules so far
    destination_nodes:
        Destination nodes so far already running netperf server

    Returns
    -------
    dependency: int
        updated dependency in case netperf is not installed
    netperf_runners: List[NetperfRunner]
        all the netperf flows generated
    workers: List[multiprocessing.Process]
        Processes to run netperf flows
    ss_schedules: dict
        updated ss_schedules
    """
    netperf_runners = []
    if not dependency:
        logger.warning("Netperf not found. Tcp flows cannot be generated")
    else:
        # Get flow attributes
        [
            src_ns,
            dst_ns,
            dst_addr,
            start_t,
            stop_t,
            n_flows,
            options,
        ] = flow._get_props()  # pylint: disable=protected-access

        # Run netserver if not already run before on given dst_node
        if dst_ns not in destination_nodes:
            NetperfRunner.run_netserver(dst_ns)

        src_name = TopologyMap.get_namespace(src_ns)["name"]

        netperf_options = {}
        netperf_options["testname"] = "TCP_STREAM"
        netperf_options["cong_algo"] = options["cong_algo"]
        f_flow = "flow" if n_flows == 1 else "flows"
        logger.info(
            "Running %s netperf %s from %s to %s...",
            n_flows,
            f_flow,
            src_name,
            dst_addr,
        )

        # Create new processes to be run simultaneously
        for _ in range(n_flows):
            runner_obj = NetperfRunner(
                src_ns, dst_addr, start_t, stop_t - start_t, dst_ns, **netperf_options
            )
            netperf_runners.append(runner_obj)

        # Find the start time and stop time to run ss command in `src_ns` to a `dst_addr`
        ss_schedules = _get_start_stop_time_for_ss(
            src_ns, dst_ns, dst_addr, start_t, stop_t, ss_schedules
        )

    return netperf_runners, ss_schedules


def setup_udp_flows(dependency, flow, destination_nodes):
    """
    Setup iperf3 to run udp flows

    Parameters
    ----------
    dependency: int
        whether iperf3 is installed
    flow: Flow
        Flow parameters
    destination_nodes:
        Destination nodes so far already running iperf3 server

    Returns
    -------
    dependency: int
        updated dependency in case iproute2 is not installed
    iperf3_runners: List[NetperfRunner]
        all the iperf3 udp flows generated
    workers: List[multiprocessing.Process]
        Processes to run iperf3 udp flows
    """
    iperf3_runners = []
    if not dependency:
        logger.warning("Iperf3 not found. Udp flows cannot be generated")
    else:
        # Get flow attributes
        [
            src_ns,
            dst_ns,
            dst_addr,
            start_t,
            stop_t,
            n_flows,
            options,
        ] = flow._get_props()  # pylint: disable=protected-access

        # Run iperf3 server if not already run before on given dst_node
        if dst_ns not in destination_nodes:
            Iperf3Runner.run_server(dst_ns)

        src_name = TopologyMap.get_namespace(src_ns)["name"]
        f_flow = "flow" if n_flows == 1 else "flows"
        logger.info(
            "Running %s udp %s from %s to %s...", n_flows, f_flow, src_name, dst_addr
        )

        runner_obj = Iperf3Runner(
            src_ns,
            dst_addr,
            options["target_bw"],
            n_flows,
            start_t,
            stop_t - start_t,
            dst_ns,
        )
        iperf3_runners.append(runner_obj)

    return iperf3_runners


def setup_ss_runners(dependency, ss_schedules, ss_filter):
    """
    setup SsRunners for collecting tcp socket statistics

    Parameters
    ----------
    dependency: int
        whether ss is installed
    ss_schedules: dict
        start time and end time for SsRunners

    Returns
    -------
    workers: List[multiprocessing.Process]
        Processes to run ss at nodes
    runners: List[SsRunners]
    """
    runners = []
    if dependency:
        logger.info("Running ss on nodes...")
        for key, timings in ss_schedules.items():
            src_ns = key[0]
            dst_ns = key[1]
            dst_addr = key[2]
            ss_runner = SsRunner(
                src_ns,
                dst_addr,
                timings[0],
                timings[1] - timings[0],
                dst_ns,
                ss_filter=ss_filter,
            )
            runners.append(ss_runner)
    else:
        logger.warning("ss not found. Sockets stats will not be collected")
    return runners


def setup_tc_runners(dependency, qdisc_stats, exp_end):
    """
    setup TcRunners for collecting qdisc statistics

    Parameters
    ----------
    dependency: int
        whether tc is installed
    qdisc_stats: dict
        info regarding nodes to run tc on
    exp_end: float
        time to stop running tc
    Returns
    -------
    workers: List[multiprocessing.Process]
        Processes to run tc at nodes
    runners: List[TcRunners]
    """
    runners = []
    if dependency and len(qdisc_stats) > 0:
        logger.info("Running tc on requested interfaces...")
        for qdisc_stat in qdisc_stats:
            tc_runner = TcRunner(
                qdisc_stat["ns_id"], qdisc_stat["int_id"], qdisc_stat["qdisc"], exp_end
            )
            runners.append(tc_runner)
    elif not dependency:
        logger.warning("tc not found. Qdisc stats will not be collected")
    return runners


def setup_ping_runners(dependency, ping_schedules):
    """
    setup PingRunners for collecting latency

    Parameters
    ----------
    dependency: int
        whether ping is installed
    ping_schedules: dict
        start time and end time for PingRunners

    Returns
    -------
    workers: List[multiprocessing.Process]
        Processes to run ss at nodes
    runners: List[PingRunner]
    """
    runners = []
    if dependency:
        for key, timings in ping_schedules.items():
            src_ns = key[0]
            dst_ns = key[1]
            dst_addr = key[2]
            ping_runner = PingRunner(
                src_ns, dst_addr, timings[0], timings[1] - timings[0], dst_ns
            )
            runners.append(ping_runner)
    else:
        logger.warning("ping not found.")
    return runners


def progress_bar(stop_time, precision=1):
    """
    Show a progress bar from from 0 `units` to `stop_time`

    The time unit is decided by `precision` in seconds. It is
    1s by default.

    Parameters
    -----------
    stop_time : int
        The time needed 100% completion
    precision : int
        Time unit for updating progress bar. 1 second be default
    """

    print()
    for _ in tqdm(range(0, stop_time, precision), desc="Experiment Progress"):
        sleep(precision)
    print()


def cleanup():
    """
    Clean up
    """
    # Remove results of the experiment
    SsResults.remove_all_results()
    NetperfResults.remove_all_results()
    TcResults.remove_all_results()
    PingResults.remove_all_results()

    kill_processes()


# Helper methods
# pylint: disable=too-many-arguments
def _get_start_stop_time_for_ss(
    src_ns, dst_ns, dst_addr, start_t, stop_t, ss_schedules
):
    """
    Find the start time and stop time to run ss command in node `src_ns`
    to a `dst_addr`

    Parameters
    ----------
    src_ns: str
        ss run from `src_ns`
    dst_ns: str
        destination network namespace for ss
    dst_addr: str
        Destination address
    start_t: int
        Start time of ss command
    stop_t: int
        Stop time of ss command
    ss_schedules: list
        List with ss command schedules

    Returns
    -------
    List: Updated ss_schedules
    """
    if (src_ns, dst_ns, dst_addr) not in ss_schedules:
        ss_schedules[(src_ns, dst_ns, dst_addr)] = (start_t, stop_t)
    else:
        (min_start, max_stop) = ss_schedules[(src_ns, dst_ns, dst_addr)]
        ss_schedules[(src_ns, dst_ns, dst_addr)] = (
            min(min_start, start_t),
            max(max_stop, stop_t),
        )

    return ss_schedules
