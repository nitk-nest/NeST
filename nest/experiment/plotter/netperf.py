# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""Plot netperf results"""

import logging
import matplotlib.pyplot as plt
import pandas as pd
from nest import config
from nest.experiment.interrupts import handle_keyboard_interrupt
from ..pack import Pack
from .common import simple_plot, mix_plot, simple_gnu_plot, mix_gnu_plot

logger = logging.getLogger(__name__)


def _plot_netperf_flow(flow, node, dest, dat_list_flows=None):
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
    if dat_list_flows is None:
        dat_list_flows = []

    # "meta" item will always be present, hence `<= 1`
    if len(flow) <= 1:
        logger.warning(
            "Flow from %s to destination %s " "doesn't have any parsed netperf result.",
            node,
            dest,
        )
        return None

    # First item is the "meta" item with user given information
    destination_node = flow[0]["destination_node"]

    # "Bias" actual start_time in experiment with user given start time
    start_time = float(flow[1]["timestamp"]) - float(flow[0]["start_time"])

    timestamp = []
    sending_rate = []

    for data in flow[1:]:
        sending_rate.append(float(data["sending_rate"]))
        # add relative time in timestamp
        timestamp.append(float(data["timestamp"]) - start_time)

    legend_string = f"{node} to {destination_node} ({dest})"

    # TODO: Check if sending_rate is always in Mbps
    fig = simple_plot(
        "",
        timestamp,
        sending_rate,
        ["Time (Seconds)", "Sending Rate (Mbps)"],
        legend_string=legend_string,
    )

    base_filename = f"sending_rate_{node}_to_{destination_node}({dest})"
    Pack.dump_plot("netperf", f"{base_filename}.png", fig)
    plt.close(fig)
    if config.get_value("enable_gnuplot"):
        data_frame = pd.DataFrame(list(zip(timestamp, sending_rate)))
        Pack.dump_datfile("netperf", f"{base_filename}.dat", data_frame)

        # Store paths in a dict for .dat, .eps and .plt
        paths = {
            "dat": Pack.get_path("netperf", f"{base_filename}.dat"),
            "eps": Pack.get_path("netperf", f"{base_filename}.eps"),
            "plt": Pack.get_path("netperf", f"{base_filename}.plt"),
        }
        simple_gnu_plot(
            paths,
            ["Time (Seconds)", "Sending Rate (Mbps)"],
            legend_string,
        )
        dat_list_flows.append(paths["dat"])

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
                if config.get_value("enable_gnuplot"):
                    plotted_data = _plot_netperf_flow(flow, node, dest, dat_list_flows)
                else:
                    plotted_data = _plot_netperf_flow(flow, node, dest)
                if plotted_data is not None:
                    all_flow_data.append(plotted_data)

        if len(all_flow_data) > 1:
            fig = mix_plot(
                "",
                all_flow_data,
                ["Time (Seconds)", "Sending Rate (Mbps)"],
                with_sum=True,
            )
            base_filename = f"sending_rate_{node}"
            Pack.dump_plot("netperf", f"{base_filename}.png", fig)
            plt.close(fig)

            if config.get_value("enable_gnuplot"):
                paths = {
                    "eps": Pack.get_path("netperf", f"{base_filename}.eps"),
                    "plt": Pack.get_path("netperf", f"{base_filename}.plt"),
                }
                legend_list = []
                for chunk in all_flow_data:
                    legend_list.append(chunk["label"])
                mix_gnu_plot(
                    dat_list_flows,
                    paths,
                    ["Time (Seconds)", "Sending Rate (Mbps)"],
                    legend_list,
                )
