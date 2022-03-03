# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Plot netperf results"""

import logging
import matplotlib.pyplot as plt
from nest.experiment.interrupts import handle_keyboard_interrupt
from ..pack import Pack
from .common import simple_plot, mix_plot

logger = logging.getLogger(__name__)


def _plot_netperf_flow(flow, node, dest):
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

    Returns
    -------
    tuple/None
        Timestamped sending_rate values
    """
    # "meta" item will always be present, hence `<= 1`
    if len(flow) <= 1:
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

        all_flow_data = []
        for connection in node_data:
            for dest in connection:
                flow = connection[dest]
                plotted_data = _plot_netperf_flow(flow, node, dest)
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
