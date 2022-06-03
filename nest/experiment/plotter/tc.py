# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Plot tc results"""

import logging
import matplotlib.pyplot as plt
import pandas as pd  # pylint: disable=import-error
from nest import config
from .common import simple_plot, simple_gnu_plot
from ..pack import Pack

logger = logging.getLogger(__name__)

# pylint: disable=too-many-locals
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
        # pylint: disable=implicit-str-concat
        logger.warning(
            "Qdisc at %s of %s doesn't have any " "parsed tc result.", interface, node
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
            "Time (Seconds)",
            param,
            legend_string=f"Interface {interface} in {node}",
        )
        filename = f"{node}_{interface}_{qdisc}_{param}.png"
        Pack.dump_plot("tc", filename, fig)
        plt.close(fig)
        if config.get_value("gnu_enable"):
            data_tuples = list(zip(timestamp, stats_params[param]))
            data_frame = pd.DataFrame(data_tuples)
            filename_dat = f"{node}_{interface}_{qdisc}_{param}.dat"
            Pack.dump_datfile("tc", filename_dat, data_frame)
            filename_eps = f"{node}_{interface}_{qdisc}_{param}.eps"
            filename_plt = f"{node}_{interface}_{qdisc}_{param}.plt"
            path_dat = Pack.get_path("tc", filename_dat)
            path_eps = Pack.get_path("tc", filename_eps)
            path_plt = Pack.get_path("tc", filename_plt)
            legend_string = f"Interface {interface} in {node}"
            simple_gnu_plot(
                path_dat,
                path_plt,
                path_eps,
                "Time (Seconds)",
                param,
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
