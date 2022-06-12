# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Plot netperf results"""

import logging
import matplotlib.pyplot as plt
import pandas as pd  # pylint: disable=import-error
from nest import config
from nest.experiment.interrupts import handle_keyboard_interrupt
from ..pack import Pack
from .common import simple_plot, mix_plot, simple_gnu_plot, mix_gnu_plot

logger = logging.getLogger(__name__)

# pylint: disable=too-many-locals
def _plot_netperf_flow(flow, node, dest, dat_list_flows):
    """
    Plot netperf stats of the flow

    Parameters
    ----------
    exp_name : str
        Name of experiment for which results were obtained
    flow : List
        List with timestamps and stats
    node : str
        Node from which netperf results were obtained from
    dest :
        Destination ip:port address of the flow
    dat_list_flows :
        Store dat files name of all flows along with their path.

    Returns
    -------
    tuple/None
        Timestamped sending_rate values
    """
    # "meta" item will always be present, hence `<= 1`
    if len(flow) <= 1:
        # pylint: disable=implicit-str-concat
        logger.warning(
            "Flow from %s to destination %s " "doesn't have any parsed netperf result.",
            node,
            dest,
        )
        return None

    # First item is the "meta" item with user given information
    user_given_start_time = float(flow[0]["start_time"])
    destination_node = flow[0]["destination_node"]

    # "Bias" actual start_time in experiment with user given start time
    start_time = float(flow[1]["timestamp"]) - user_given_start_time

    timestamp = []
    sending_rate = []

    for data in flow[1:]:
        sending_rate.append(float(data["sending_rate"]))
        relative_time = float(data["timestamp"]) - start_time
        timestamp.append(relative_time)

    legend_string = f"{node} to {destination_node} ({dest})"

    # TODO: Check if sending_rate is always in Mbps
    fig = simple_plot(
        "",
        timestamp,
        sending_rate,
        "Time (Seconds)",
        "Sending Rate (Mbps)",
        legend_string=legend_string,
    )

    filename = f"sending_rate_{node}_to_{destination_node}({dest}).png"
    Pack.dump_plot("netperf", filename, fig)
    plt.close(fig)
    if config.get_value("enable_gnuplot"):
        data_tuples = list(zip(timestamp, sending_rate))
        data_frame = pd.DataFrame(data_tuples)
        filename_dat = f"sending_rate_{node}_to_{destination_node}({dest}).dat"
        Pack.dump_datfile("netperf", filename_dat, data_frame)
        filename_eps = f"sending_rate_{node}_to_{destination_node}({dest}).eps"
        filename_plt = f"sending_rate_{node}_to_{destination_node}({dest}).plt"
        path_plt = Pack.get_path("netperf", filename_plt)
        path_dat = Pack.get_path("netperf", filename_dat)
        path_eps = Pack.get_path("netperf", filename_eps)
        simple_gnu_plot(
            path_dat,
            path_plt,
            path_eps,
            "Time (Seconds)",
            "Sending Rate (Mbps)",
            legend_string,
        )
        dat_list_flows.append(path_dat)

    return {"label": legend_string, "values": (timestamp, sending_rate)}


@handle_keyboard_interrupt
def plot_netperf(parsed_data):
    """
    Plot statistics obtained from netperf

    Parameters
    ----------
    exp_name : str
        Name of experiment for which results were obtained
    parsed_data : Dict
        JSON data parsed from ss
    """
    for node in parsed_data:
        node_data = parsed_data[node]

        # this store dat files name of all flows along with their path.
        dat_list_flows = []
        all_flow_data = []
        for connection in node_data:
            for dest in connection:
                flow = connection[dest]
                plotted_data = _plot_netperf_flow(flow, node, dest, dat_list_flows)
                if plotted_data is not None:
                    all_flow_data.append(plotted_data)

        if len(all_flow_data) > 1:
            fig = mix_plot(
                "",
                all_flow_data,
                "Time (Seconds)",
                "Sending Rate (Mbps)",
                with_sum=True,
            )
            filename = f"sending_rate_{node}.png"
            Pack.dump_plot("netperf", filename, fig)
            plt.close(fig)

            if config.get_value("enable_gnuplot"):
                filename_eps = f"sending_rate_{node}.eps"
                path_eps = Pack.get_path("netperf", filename_eps)
                filename_plt = f"sending_rate_{node}.plt"
                path_plt = Pack.get_path("netperf", filename_plt)
                legend_list = []
                for chunk in all_flow_data:
                    legend_list.append(chunk["label"])
                mix_gnu_plot(
                    dat_list_flows,
                    path_plt,
                    path_eps,
                    "Time (Seconds)",
                    "Sending Rate (Mbps)",
                    legend_list,
                )
