# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""Script to be run for running experiments on topology"""

from multiprocessing import Process
from collections import namedtuple, defaultdict
import logging
import os
from time import sleep
import copy
from tqdm import tqdm

from nest.logging_helper import DepedencyCheckFilter
from nest import config
from nest.topology_map import TopologyMap
from nest.clean_up import kill_processes, tcp_modules_clean_up
from nest import engine
from .pack import Pack

# Import results
from .results import (
    Iperf3ServerResults,
    SsResults,
    NetperfResults,
    Iperf3Results,
    TcResults,
    PingResults,
    CoAPResults,
)

# Import parsers
from .parser.ss import SsRunner
from .parser.netperf import NetperfRunner
from .parser.iperf3 import Iperf3Runner, Iperf3ServerRunner
from .parser.tc import TcRunner
from .parser.ping import PingRunner
from .parser.coap import CoAPRunner

# Import plotters
from .plotter.ss import plot_ss
from .plotter.netperf import plot_netperf
from .plotter.iperf3 import plot_iperf3
from .plotter.tc import plot_tc
from .plotter.ping import plot_ping
from ..engine.util import is_dependency_installed, is_package_installed

logger = logging.getLogger(__name__)
if not any(isinstance(filter, DepedencyCheckFilter) for filter in logger.filters):
    # Duplicate filter is added to avoid logging of same error
    # messages incase any of the tools is not installed
    logger.addFilter(DepedencyCheckFilter())

# pylint: disable=too-many-locals, too-many-branches
# pylint: disable=too-many-statements, invalid-name
def run_experiment(exp):
    """
    Run experiment

    Parameters
    -----------
    exp : Experiment
        The experiment attributes
    """

    tcp_modules_helper(exp)
    tools = ["netperf", "ss", "tc", "iperf3", "ping", "coap", "server"]
    Runners = namedtuple("runners", tools)
    exp_runners = Runners(
        netperf=[], ss=[], tc=[], iperf3=[], ping=[], coap=[], server=[]
    )  # Runner objects

    # Keep track of all destination nodes [to ensure netperf, iperf3 and
    # coap server is run at most once]
    destination_nodes = {"netperf": set(), "iperf3": set(), "coap": set()}

    # Contains start time and end time to run respective command
    # from a source netns to destination address (in destination netns)
    ss_schedules = defaultdict(lambda: (float("inf"), float("-inf")))
    ping_schedules = defaultdict(lambda: (float("inf"), float("-inf")))

    # Overall experiment stop time considering all flows
    exp_end_t = float("-inf")

    dependencies = get_dependency_status(tools)

    ss_required = False
    ss_filters = set()
    server_runner = []

    # Traffic generation
    for flow in exp.flows:
        iperf3_options = {}
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
            ss_required = True

            if options["tool"] == "netperf":
                # * Ignore netperf tcp control connections
                # * Destination port of netperf control connection is 12865
                # * We also have "sport" (source port) in the below condition since
                #   there can be another flow in the reverse direction whose control
                #   connection also we must ignore.
                ss_filters.add("sport != 12865 and dport != 12865")

                (tcp_runners, ss_schedules,) = setup_tcp_flows(
                    dependencies["netperf"],
                    flow,
                    ss_schedules,
                    destination_nodes["netperf"],
                )
                exp_runners.netperf.extend(tcp_runners)
                # Update destination nodes
                destination_nodes["netperf"].add(dst_ns)

            elif options["tool"] == "iperf3":
                ss_filters.add("sport != 5201 and dport != 5201")
                (tcp_runners, ss_schedules,) = setup_tcp_flows(
                    dependencies["iperf3"],
                    flow,
                    ss_schedules,
                    destination_nodes["iperf3"],
                )
                exp_runners.iperf3.extend(tcp_runners)
                # Update destination nodes
                destination_nodes["iperf3"].add(dst_ns)

                dst_port_options = {}
                port_nos = options["port_nos"]
                for port_no in port_nos:
                    options["port_no"] = port_no
                    dst_port_options[port_no] = copy.deepcopy(options)

                if dst_ns in iperf3_options:
                    dst_port_options.update(iperf3_options.get(dst_ns))
                iperf3_options.update({dst_ns: dst_port_options})

        elif options["protocol"] == "udp":
            # * Ignore iperf3 tcp control connections
            # * Destination port of iperf3  control connection is 5201
            # * We also have "sport" (source port) in the below condition since
            #   there can be another flow in the reverse direction whose control
            #   connection also we must ignore.
            ss_filters.add("sport != 5201 and dport != 5201")
            udp_runners = setup_udp_flows(dependencies["iperf3"], flow)

            exp_runners.iperf3.extend(udp_runners)

            # Update destination nodes
            destination_nodes["iperf3"].add(dst_ns)
            dst_port_options = {options["port_no"]: options}
            if dst_ns in iperf3_options:
                dst_port_options.update(iperf3_options.get(dst_ns))
            iperf3_options.update({dst_ns: dst_port_options})

        server_runner.extend(run_server(iperf3_options, exp_end_t, options["protocol"]))

    for coap_application in exp.coap_applications:
        [
            src_ns,
            dst_ns,
            dst_addr,
            _,
            _,
            _,
        ] = coap_application._get_props()  # pylint: disable=protected-access

        config.set_value("show_progress_bar", False)

        # Setup runners for emulating CoAP traffic
        coap_runners = setup_coap_runners(
            dependencies["coap"], coap_application, destination_nodes["coap"]
        )
        exp_runners.coap.extend(coap_runners)
        destination_nodes["coap"].add(dst_ns)

    if ss_required:
        ss_filter = " and ".join(ss_filters)
        ss_runners = setup_ss_runners(dependencies["ss"], ss_schedules, ss_filter)
        exp_runners.ss.extend(ss_runners)

    tc_runners = setup_tc_runners(dependencies["tc"], exp.qdisc_stats, exp_end_t)
    exp_runners.tc.extend(tc_runners)

    ping_runners = setup_ping_runners(dependencies["ping"], ping_schedules)
    exp_runners.ping.extend(ping_runners)

    try:
        # Start traffic generation
        run_workers(setup_flow_workers(exp_runners, exp_end_t))

        logger.info("Parsing statistics...")

        exp_runners.server.extend(server_runner)

        # Parse the stored statistics
        run_workers(setup_parser_workers(exp_runners))

        logger.info("Parsing statistics complete!")
        logger.info("Output results as JSON dump...")

        # Output results as JSON dumps
        dump_json_ouputs()

        if config.get_value("readme_in_stats_folder"):
            # Copying README.txt to stats folder
            relative_path = os.path.join("info", "README.txt")
            readme_path = os.path.join(os.path.dirname(__file__), relative_path)
            Pack.copy_files(readme_path)

        if config.get_value("plot_results"):
            logger.info("Plotting results...")

            # Plot results and dump them as images
            run_workers(setup_plotter_workers())

            logger.info("Plotting complete!")

        logger.info("Experiment %s complete!", exp.name)

    except KeyboardInterrupt:
        logger.warning(
            "Experiment %s forcefully stopped. The results obtained maybe incomplete!",
            exp.name,
        )
    finally:
        cleanup()


def tcp_modules_helper(exp):
    """
    This function is called at the beginning of run_experiment
    to perform tcp modules related helper tasks

    Parameters
    -----------
    exp : Experiment
        The experiment attributes
    """
    if exp.tcp_module_params:
        if (
            not (config.get_value("show_tcp_module_parameter_confirmation"))
            or input(
                "Are you sure you want to modify TCP module parameters in Linux kernel? (y/n) : "
            ).lower()
            == "y"
        ):
            for cong_algo, params in exp.tcp_module_params.items():
                flag = engine.is_module_loaded(cong_algo)
                if flag:
                    # the module is already loaded, so store the old parameters
                    # during experiment set these parameters with new values (reset=False)
                    # during cleanup reset these parameters with old values (reset=True)
                    exp.old_cong_algos[cong_algo] = engine.get_current_params(cong_algo)
                    engine.set_tcp_params(cong_algo, params, False)
                else:
                    # the module will be newly loaded
                    # it should be removed during cleanup
                    (exp.new_cong_algos).append(cong_algo)
                    params_string = " ".join(
                        {f"{key}={value}" for key, value in params.items()}
                    )
                    engine.load_tcp_module(cong_algo, params_string)


def run_server(iperf3options, exp_end_t, protocol):
    """
    Run and wait for all server to start

    Parameters
    ----------
    iperf3options: dict
        start server with iperf3 server options
    exp_end_t: int
        experiment completion time
    protocol: str
        transport layer protocol, either "tcp" or "udp"
    """
    # Start server
    server_list = []
    for dst_ns in iperf3options:
        for dst_port in iperf3options[dst_ns]:
            runner_obj = Iperf3ServerRunner(dst_ns, exp_end_t, protocol)
            runner_obj.setup_iperf3_server(iperf3options[dst_ns][dst_port])
            server_list.append(runner_obj)

    for server in server_list:
        process = Process(target=server.run)
        process.start()

    return server_list


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
    CoAPResults.output_to_file()
    Iperf3ServerResults.output_to_file()


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

    for coap_runner in exp_runners.coap:
        parsers.append(Process(target=coap_runner.parse))

    for server_runner in exp_runners.server:
        parsers.append(Process(target=server_runner.parse))

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
        # Check for the availability of aiocoap for CoAP emulation
        if dependency == "coap":
            dependencies[dependency] = is_package_installed("aiocoap")
            continue
        dependencies[dependency] = is_dependency_installed(dependency)
    return dependencies


def setup_tcp_flows(dependency, flow, ss_schedules, destination_nodes):
    """
    Setup netperf/iperf3 to run tcp flows
    Parameters
    ----------
    dependency: int
        whether netperf/iperf3 is installed
    flow: Flow
        Flow parameters
    ss_schedules:
        ss_schedules so far
    destination_nodes:
        Destination nodes so far already running netperf/iperf3 server

    Returns
    -------
    dependency: int
        updated dependency in case netperf/iperf3 is not installed
    tcp_runners: List[NetperfRunner] / List[Iperf3Runner]
        all the netperf/iperf3 flows generated
    workers: List[multiprocessing.Process]
        Processes to run netperf/iperf3 flows
    ss_schedules: dict
        updated ss_schedules
    """
    tcp_runners = []
    if not dependency:
        logger.warning("Dependency not found. Tcp flows cannot be generated")
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

        if options["tool"] == "netperf":
            # Run netserver if not already run before on given dst_node
            if dst_ns not in destination_nodes:
                NetperfRunner.run_netserver(dst_ns)

            src_name = TopologyMap.get_node(src_ns).name

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
                    src_ns,
                    dst_addr,
                    start_t,
                    stop_t - start_t,
                    dst_ns,
                    **netperf_options,
                )
                tcp_runners.append(runner_obj)

        elif options["tool"] == "iperf3":
            src_name = TopologyMap.get_node(src_ns).name
            f_flow = "flow" if n_flows == 1 else "flows"
            iperf3_options = {}
            iperf3_options["cong_algo"] = options["cong_algo"]
            logger.info(
                "Running %s tcp iperf3 %s from %s to %s...",
                n_flows,
                f_flow,
                src_name,
                dst_addr,
            )

            port_nos = options["port_nos"]

            # Create new processes to be run simultaneously
            for i in range(n_flows):
                runner_obj = Iperf3Runner(
                    src_ns,
                    dst_addr,
                    options["target_bw"],
                    1,
                    start_t,
                    stop_t - start_t,
                    dst_ns,
                    "tcp",
                    **iperf3_options,
                )
                options["port_no"] = port_nos[i]
                runner_obj.setup_iperf3_client(options)
                tcp_runners.append(runner_obj)

        # Find the start time and stop time to run ss command in `src_ns` to a `dst_addr`
        ss_schedules = _get_start_stop_time_for_ss(
            src_ns, dst_ns, dst_addr, start_t, stop_t, ss_schedules
        )
    return tcp_runners, ss_schedules


def setup_udp_flows(dependency, flow):
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

        src_name = TopologyMap.get_node(src_ns).name
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
            "udp",
        )
        runner_obj.setup_iperf3_client(options)
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


def setup_coap_runners(dependency, application, destination_nodes):
    """
    Setup CoAPRunner objects for generating CoAP traffic

    Parameters
    ----------
    dependency : int
        Whether aiocoap is installed
    application : CoapApplication
        The CoapApplication object
    destination_nodes:
        Destination nodes so far already running CoAP server

    Returns
    -------
    runners : List[CoAPRunner]
        List of CoAPRunner objects for the current flow object
    """
    runners = []

    # If aiocoap is installed
    if dependency:
        # Get flow attributes
        [
            src_ns,
            dst_ns,
            dst_addr,
            n_con_msgs,
            n_non_msgs,
            user_options,
        ] = application._get_props()  # pylint: disable=protected-access

        # Run CoAP server if not already run before on given dst_node
        if dst_ns not in destination_nodes:

            # If user has not supplied the user options
            if user_options is not None:
                # Creating the options string for running the CoAP server
                if (
                    "coap_server_content" in user_options.keys()
                    and user_options["coap_server_content"] != ""
                ):
                    server_content = '"' + user_options["coap_server_content"] + '"'
                    server_options = f"-c {server_content}"
                else:
                    server_options = None
            else:
                server_options = None

            # Running the server
            CoAPRunner.run_server(dst_ns, server_options)

        # Create the CoAPRunner object
        coap_runner = CoAPRunner(src_ns, dst_addr, user_options, n_con_msgs, n_non_msgs)
        runners.append(coap_runner)

    # If aiocoap is not installed
    else:
        logger.warning("aiocoap not found for CoAP emulation.")

    # Return the list of runners
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
    try:
        print()
        for _ in tqdm(range(0, stop_time, precision), desc="Experiment Progress"):
            sleep(precision)
        print()
    except KeyboardInterrupt:
        logger.debug(
            "ProgressBar process received KeyboardInterrupt. Stopping it gracefully."
        )

    logger.info("Cleaning up all the spawned child processes...")


def cleanup():
    """
    Clean up
    """
    # Remove results of the experiment
    SsResults.remove_all_results()
    NetperfResults.remove_all_results()
    TcResults.remove_all_results()
    PingResults.remove_all_results()
    CoAPResults.remove_all_results()
    Iperf3Results.remove_all_results()
    Iperf3ServerResults.remove_all_results()

    # Clean up the configured TCP modules and kill processes
    tcp_modules_clean_up()
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
