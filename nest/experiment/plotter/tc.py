# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""Plot tc results"""

import logging
import matplotlib.pyplot as plt
import pandas as pd
from nest import config
from .common import simple_plot, simple_gnu_plot
from ..pack import Pack

logger = logging.getLogger(__name__)


def _extract_from_tc_stats(stats, node, interface):
    """
    Extract information from tc stats and convert it to
    conveniently plottable data format

    Parameters
    ----------
    stats : List
        List of timestamps and stats
    node : str
        Node from which tc results were obtained from
    interface : str
        Interface from which results were obtained from
    """
    if len(stats) == 0:
        logger.warning(
            "Qdisc at %s of %s doesn't have any parsed tc result.", interface, node
        )
        return None

    qdisc = stats[0]["kind"]
    start_time = float(stats[0]["timestamp"])

    timestamp = []
    stats_params = {}

    for param in stats[0]:
        if param not in ("timestamp", "kind"):
            stats_params[param] = []

    for data in stats:
        for param, param_data in stats_params.items():
            param_data.append(data[param])
        relative_time = float(data["timestamp"]) - start_time
        timestamp.append(relative_time)

    return (qdisc, timestamp, stats_params)


def _plot_tc_stats(stats, node, interface):
    """
    Plot tc stats of the flow

    Parameters
    ----------
    exp_name : str
        Name of experiment for which results were obtained
    stats : List
        List with timestamps and stats
    node : str
        Node from which tc results were obtained from
    interface : str
        Interface from which results were obtained from
    """
    values = _extract_from_tc_stats(stats, node, interface)
    if values is None:
        return
    (qdisc, timestamp, stats_params) = values

    for param in stats_params:
        fig = simple_plot(
            "Traffic Control (tc) Statistics",
            timestamp,
            stats_params[param],
            ["Time (Seconds)", param],
            legend_string=f"Interface {interface} in {node}",
        )
        base_filename = f"{node}_{interface}_{qdisc}_{param}"
        Pack.dump_plot("tc", f"{base_filename}.png", fig)
        plt.close(fig)

        if config.get_value("enable_gnuplot"):
            data_frame = pd.DataFrame(list(zip(timestamp, stats_params[param])))
            Pack.dump_datfile("tc", f"{base_filename}.dat", data_frame)

            # Store paths in a dict for .dat, .eps and .plt
            paths = {
                "dat": Pack.get_path("tc", f"{base_filename}.dat"),
                "eps": Pack.get_path("tc", f"{base_filename}.eps"),
                "plt": Pack.get_path("tc", f"{base_filename}.plt"),
            }

            legend_string = f"Interface {interface} in {node}"
            simple_gnu_plot(
                paths,
                ["Time (Seconds)", param],
                legend_string,
                "Traffic Control (tc) Statistics",
            )


def plot_tc(parsed_data):
    """
    Plot statistics obtained from tc

    Parameters
    ----------
    exp_name : str
        Name of experiment for which results were obtained
    parsed_data : Dict
        JSON data parsed from ss
    """
    for node in parsed_data:
        node_data = parsed_data[node]
        for interfaces in node_data:
            for interface in interfaces:
                qdisc = interfaces[interface]
                for handle in qdisc:
                    stats = qdisc[handle]
                    _plot_tc_stats(stats, node, interface)
