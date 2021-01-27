# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Plot netperf results"""

import logging
import matplotlib.pyplot as plt

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

    # "Bias" actual start_time in experiment with user given start time
    start_time = float(flow[1]["timestamp"]) - user_given_start_time

    timestamp = []
    sending_rate = []

    for data in flow[1:]:
        sending_rate.append(float(data["sending_rate"]))
        relative_time = float(data["timestamp"]) - start_time
        timestamp.append(relative_time)

    # TODO: Check if sending_rate is always in Mbps
    fig = simple_plot(
        "Netperf",
        timestamp,
        sending_rate,
        "Time (s)",
        "Sending rate (Mbps)",
        legend_string=f"{node} to {dest}",
    )

    filename = "{node}_{dest}_sending_rate.png".format(node=node, dest=dest)
    Pack.dump_plot("netperf", filename, fig)
    plt.close(fig)

    return (timestamp, sending_rate)


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
                values = _plot_netperf_flow(flow, node, dest)
                if values is not None:
                    all_flow_data.append(
                        {"label": f"{node} to {dest}", "values": values}
                    )

        if len(all_flow_data) > 1:
            fig = mix_plot(
                "Netperf",
                all_flow_data,
                "Time (s)",
                "Sending rate (Mbps)",
                with_sum=True,
            )
            filename = f"{node}_sending_rate.png"
            Pack.dump_plot("netperf", filename, fig)
            plt.close(fig)
