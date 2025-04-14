# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2022-2025 NITK Surathkal

"""Plot httperf results"""
import logging
import time
import matplotlib.pyplot as plt
from nest.experiment.interrupts import handle_keyboard_interrupt
from ..pack import Pack
from .common import html_table, bar_plot

logger = logging.getLogger(__name__)


def _plot_httperf_flow(stat, stat_data):
    """
    Plot httperf stats of the flow

    Parameters
    ----------
    stat : str
        Name of the metric to be plotted
    stat_data: Dict
        A dictionary of the statistic data for different clients

    Returns
    -------
    tuple/None
        Timestamped comparison metric values
    """
    # if there is only one client, comparison plots can't be processed
    if len(stat_data.keys()) <= 1:
        logger.warning(
            "Comparison plot can not be processed with fewer than 2 clients."
        )
        return {}

    clients = list(stat_data.keys())
    metric_data = []
    for client in clients:
        metric_data.append(stat_data[client])

    fig = bar_plot(
        "",
        clients,
        metric_data,
        ["Clients", stat],
    )

    current_timestamp = time.time()
    filename = f"comparison_plot_for_{stat}_httperf_{current_timestamp}.png"
    Pack.dump_plot("httperf", filename, fig)
    plt.close(fig)

    return {"label": stat, "values": (clients, metric_data)}


def plot_httperf_stats_table(all_flow_data: dict):
    """
    Plot httperf stats table of the application

    Parameters
    ----------
    all_flow_data : dict
        A dictionary containing all data related to the flow.nts

    Returns
    -------
    None
        Dumps stats table into a file.
    """
    row_labels = []
    col_labels = []
    for key in all_flow_data.keys():
        row_labels.append(key)
    if len(row_labels) == 0:
        return
    for node in all_flow_data[row_labels[0]]:
        col_labels.append(node)
    table_data = [[0] * len(col_labels) for _ in range(len(row_labels))]
    for row_index in range(len(row_labels)):
        for col_index in range(len(col_labels)):
            table_data[row_index][col_index] = all_flow_data[row_labels[row_index]][
                col_labels[col_index]
            ]
    result_html_table = html_table(row_labels, col_labels, table_data)
    Pack.dump_file("httperf.html", result_html_table)


@handle_keyboard_interrupt
def plot_httperf(parsed_data):
    """
    Plot statistics obtained from httperf

    Parameters
    ----------
    parsed_data : Dict
        JSON data parsed from ss
    """
    all_flow_data = {}
    for node in parsed_data:
        node_data = parsed_data[node]
        for dest in node_data:
            for dest_addr in dest:
                dest_data = dest[dest_addr]
                if "output" in dest_data and len(dest_data["output"]) >= 1:
                    dest_output = dest_data["output"][0]
                else:
                    dest_output = None
                # Tracking total connection metrics like number of connections, requests and replies
                if "total" in dest_output and "connections" in dest_output["total"]:
                    all_flow_data.setdefault("connections", {})[node] = int(
                        dest_output["total"]["connections"]
                    )
                    all_flow_data.setdefault("requests", {})[node] = int(
                        dest_output["total"]["requests"]
                    )
                    all_flow_data.setdefault("replies", {})[node] = int(
                        dest_output["total"]["replies"]
                    )

                # Tracking errors for error comparison plot, if available
                if "Errors" in dest_output and "total" in dest_output["Errors"]:
                    all_flow_data.setdefault("Errors", {})[node] = int(
                        dest_output["Errors"]["total"]
                    )

                # Tracking request rate if available
                if "request_rate" in dest_output:
                    all_flow_data.setdefault("request_rate", {})[node] = float(
                        dest_output["request_rate"]
                    )

                # Tracking request size, if available
                if "request_size" in dest_output:
                    all_flow_data.setdefault("request_size", {})[node] = float(
                        dest_output["request_size"]
                    )

                # Tracking connection rate, if available
                if (
                    "connection" in dest_output
                    and "connection_rate" in dest_output["connection"]
                ):
                    all_flow_data.setdefault("connection_rate", {})[node] = float(
                        dest_output["connection"]["connection_rate"]
                    )

    for item in all_flow_data.items():
        _plot_httperf_flow(item[0], item[1])
    plot_httperf_stats_table(all_flow_data)
