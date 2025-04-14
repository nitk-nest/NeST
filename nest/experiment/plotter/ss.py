# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""Plot ss results"""

import logging
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd
from nest import config
from nest.experiment.interrupts import handle_keyboard_interrupt
from ..pack import Pack
from .common import simple_plot, mix_plot, simple_gnu_plot, mix_gnu_plot

logger = logging.getLogger(__name__)

# pylint: disable=too-many-branches
def _get_list_of_ss_params():
    """
    Return list of params parsed by ss
    """
    return ["cwnd", "rtt", "dev_rtt", "ssthresh", "rto", "delivery_rate", "pacing_rate"]


def _get_ss_params_units():
    """
    Obtain the units of each ss parameters
    """
    units = {
        "cwnd": "Packets",
        "rtt": "ms",
        "dev_rtt": "ms",
        "ssthresh": "Packets",
        "rto": "ms",
        "delivery_rate": "Mbps",
        "pacing_rate": "Mbps",
    }
    return units


def _get_nicer_param_names():
    """
    For example,
    'rtt' -> 'RTT'
    'delivery_rate' -> 'Delivery rate'
    """
    nice_names = {
        "cwnd": "Congestion Window",
        "rtt": "RTT",
        "dev_rtt": "Deviation in RTT",
        "ssthresh": "Slow Start Threshold",
        "rto": "TCP Retransmission Timeout",
        "delivery_rate": "Delivery Rate",
        "pacing_rate": "Pacing Rate",
    }
    return nice_names


def _get_ylabel(param):
    """
    Obtain y label for plots for a given parameter.

    For example, 'delivery_rate' -> 'Delivery rate (Mbps)'

    Arguments
    ---------
        param : str
            parameter

    Returns
    -------
        str
    """
    # Get ss param units
    units = _get_ss_params_units()
    # Get "nicer" param names
    nicer_param_names = _get_nicer_param_names()

    ylabel = nicer_param_names[param]
    if units[param] is not None:
        ylabel += f" ({units[param]})"

    return ylabel


def _extract_from_ss_flow(flow, node, dest_ip, dest_port):
    """
    Extract information from flow data and convert it to
    conveniently plottable data format

    Parameters
    ----------
    flow : List
        List with timestamps and stats
    node : string
        Node from which ss results were obtained from
    dest_ip : string
        Destination ip address of the flow
    dest_port : string
        Destination port of the flow

    Returns
    -------
    (timestamp, flow_params) or None
        Return timestamp and flow parameters
    """
    # "meta" item will always be present, hence `<= 1`
    if len(flow) <= 1:
        logger.warning(
            "Flow from %s to destination %s:%s " "doesn't have any parsed ss result.",
            node,
            dest_ip,
            dest_port,
        )
        return None

    # First item is the "meta" item with user given information
    destination_node = flow[0]["destination_node"]

    # "Bias" actual start_time in experiment with user given start time
    start_time = float(flow[1]["timestamp"]) - float(flow[0]["start_time"])

    timestamp = []
    flow_params = {}

    for param in _get_list_of_ss_params():
        flow_params[param] = []

    for data in flow[1:]:
        for stat, stat_data in flow_params.items():
            if stat in data:
                stat_data.append(float(data[stat]))
            else:
                stat_data.append(None)
        # add relative time in timestamp
        timestamp.append(float(data["timestamp"]) - start_time)

    return {"destination_node": destination_node, "values": (timestamp, flow_params)}


def _plot_ss_flow(flow, node, dest_ip, dest_port, dat_tuple_flows):
    """
    Plot ss stats of the flow with optimized variable usage.

    Parameters
    ----------
    flow : List
        List with timestamps and stats
    node : string
        Source node
    dest_ip : string
        Destination IP
    dest_port : string
        Destination port
    dat_tuple_flows : List
        List for storing (param, dat_path) tuples

    Returns
    -------
    dict
        Contains label, destination_node, and values
    """
    data = _extract_from_ss_flow(flow, node, dest_ip, dest_port)
    if data["values"] is None:
        return None

    destination_node = data["destination_node"]
    timestamp, flow_params = data["values"]
    legend_string = f"{node} to {destination_node} ({dest_ip}:{dest_port})"

    for param in flow_params:
        # Filter None values and prepare data
        filtered_data = [
            (x, y) for x, y in zip(timestamp, flow_params[param]) if y is not None
        ]

        fig = simple_plot(
            "Socket Statistics",
            [x for x, _ in filtered_data],
            [y for _, y in filtered_data],
            ["Time (Seconds)", _get_ylabel(param)],
            legend_string=legend_string,
        )

        base_filename = f"{param}_{node}_to_{destination_node}({dest_ip}:{dest_port})"
        Pack.dump_plot("ss", f"{base_filename}.png", fig)
        plt.close(fig)

        if config.get_value("enable_gnuplot"):
            Pack.dump_datfile("ss", f"{base_filename}.dat", pd.DataFrame(filtered_data))
            paths = {
                "dat": Pack.get_path("ss", f"{base_filename}.dat"),
                "eps": Pack.get_path("ss", f"{base_filename}.eps"),
                "plt": Pack.get_path("ss", f"{base_filename}.plt"),
            }

            simple_gnu_plot(
                paths,
                ["Time (Seconds)", _get_ylabel(param)],
                legend_string,
                "Socket Statistics",
            )
            dat_tuple_flows.append((param, paths["dat"]))

    return {
        "label": legend_string,
        "destination_node": destination_node,
        "values": (timestamp, flow_params),
    }


# pylint: disable=too-many-locals
@handle_keyboard_interrupt
def plot_ss(parsed_data):
    """
    Plot statistics obtained from ss

    Parameters
    ----------
    exp_name : string
        Name of experiment for which results were obtained
    parsed_data : Dict
        JSON data parsed from ss
    """

    # pylint: disable=too-many-nested-blocks
    for node in parsed_data:
        node_data = parsed_data[node]
        for connection in node_data:
            for dest_ip in connection:
                # this will store all dat files of different
                # parameters in form of pair of (param,dat_file)
                # example :dat_tuple_flows = [("cwnd",flow1_dat_name),
                #                             ("cwnd",flow2_dat_name),
                #                             ("rtt",flow1_dat_name),
                #                             ("rtt",flow12_dat_name)]
                dat_tuple_flows = []
                all_flow_data = []
                destination_node = None

                flow_data = connection[dest_ip]
                for dest_port in flow_data:
                    flow = flow_data[dest_port]
                    plotted_data = _plot_ss_flow(
                        flow, node, dest_ip, dest_port, dat_tuple_flows
                    )
                    if plotted_data is not None:
                        all_flow_data.append(
                            {
                                "label": plotted_data["label"],
                                "values": plotted_data["values"],
                            }
                        )

                        if destination_node is None:
                            destination_node = plotted_data["destination_node"]
                        elif destination_node != plotted_data["destination_node"]:
                            raise Exception(
                                "Error in plotting ss stats. Unexpected "
                                "destination node in ss.json"
                            )

                if len(all_flow_data) > 1:

                    x_vals = []
                    labels = []

                    for flow_data in all_flow_data:
                        x_vals.append(flow_data["values"][0])
                        labels.append(flow_data["label"])

                    # Dictionary which store {"cwnd":[flow1_dat_file,flow2_dat_file],
                    #                         "rtt":[flow1_dat_file,flow2_dat_file]}
                    dat_dictionary = defaultdict(list)
                    for param, path in dat_tuple_flows:
                        dat_dictionary[param].append(path)
                    for param in all_flow_data[0]["values"][1]:
                        y_vals = []
                        for flow_data in all_flow_data:
                            y_vals.append(flow_data["values"][1][param])

                        data = []

                        for i in range(len(labels)):
                            data.append(
                                {"values": (x_vals[i], y_vals[i]), "label": labels[i]}
                            )

                        fig = mix_plot(
                            "Socket Statistics",
                            data,
                            ["Time (Seconds)", _get_ylabel(param)],
                        )

                        base_filename = (
                            f"{param}_{node}_to_{destination_node}({dest_ip})"
                        )
                        Pack.dump_plot("ss", f"{base_filename}.png", fig)
                        plt.close(fig)

                        if config.get_value("enable_gnuplot"):
                            paths = {
                                "eps": Pack.get_path("ss", f"{base_filename}.eps"),
                                "plt": Pack.get_path("ss", f"{base_filename}.plt"),
                                "dat": Pack.get_path("ss", f"{base_filename}.dat"),
                            }
                            mix_gnu_plot(
                                dat_dictionary[param],
                                paths,
                                ["Time (Seconds)", _get_ylabel(param)],
                                labels,
                                "Socket Statistics",
                            )
