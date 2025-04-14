# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""Plot MPEG-DASH results"""

import logging
import matplotlib.pyplot as plt
from ..interrupts import handle_keyboard_interrupt
from ..pack import Pack
from .common import simple_plot

logger = logging.getLogger(__name__)


def _get_list_of_plot_params():
    """
    Return list of params parsed by MPEG-DASH
    """
    return ["bitrate", "bitrate_level", "throughput", "buffer", "rtt"]


def _get_plot_params_units():
    """
    Obtain the units of each MPEG-DASH parameters
    """
    units = {
        "bitrate": "Kbps",
        "bitrate_level": "Kbps",
        "throughput": "Kbps",
        "buffer": "ms",
        "rtt": "s",
    }
    return units


def _get_ylabel(param):
    """
    Obtain y label for plots for a given parameter.

    For example, 'rtt' -> 'RTT (ms)'

    Arguments
    ---------
        param : str
            parameter

    Returns
    -------
        str
    """
    # Get MPEG-DASH param units
    units = _get_plot_params_units()
    # Get "nicer" param names
    nicer_param_names = {
        "bitrate": "Bitrate",
        "bitrate_level": "Bitrate Level",
        "throughput": "Throughput",
        "buffer": "Buffer",
        "rtt": "RTT",
    }

    ylabel = nicer_param_names[param]
    if units[param] is not None:
        ylabel += f" ({units[param]})"

    return ylabel


def _extract_from_mpeg_dash(flow, node, server_ip, stats_type):
    """
    Extract information from flow data and convert it to
    conveniently plottable data format

    Parameters
    ----------
    flow : List
        List with stats
    node : string
        The MPEG-DASH client node.
    server_ip : string
        IP Address of the MPEG-DASH server
    stats_type : string
        The type of stats for which plots are required. Can be 'Audio' or 'Video'.

    Returns
    -------
    flow_params or None
        Return flow parameters
    """
    # "meta" item will always be present, hence `<= 1`
    if len(flow) <= 1:
        logger.warning(
            "MPEG-DASH application from server %s to client %s doesn't have any parsed %s result.",
            server_ip,
            node,
            stats_type.lower(),
        )
        return None

    # First item is the "meta" item with user given information
    server_node = flow[0]["server_node"]

    chunk_numbers = []
    flow_params = {}

    for param in _get_list_of_plot_params():
        flow_params[param] = []
    for data in flow[1:]:
        for stat, stat_data in flow_params.items():
            if stat in data:
                stat_data.append(float(data[stat]))
            else:
                stat_data.append(None)
        chunk_numbers.append(data["chunk_number"])

    return {"server_node": server_node, "values": (chunk_numbers, flow_params)}


# pylint: disable=inconsistent-return-statements
def _plot_mpeg_dash(flow, node, server_ip, stats_type):
    """
    Plot MPEG-DASH stats

    Parameters
    ----------
    flow : List
        List with stats
    node : string
        The MPEG-DASH client node.
    server_ip : string
        IP Address of the MPEG-DASH server
    stats_type : string
        The type of stats for which plots are required. Can be 'Audio' or 'Video'.
    """
    data = _extract_from_mpeg_dash(flow, node, server_ip, stats_type)
    if data is None or data["values"] is None:
        return

    server_node = data["server_node"]
    (chunk_numbers, flow_params) = data["values"]

    legend_string = f"Server {server_node} to client {node}"
    for param in flow_params:
        fig = simple_plot(
            f"MPEG-DASH {stats_type} Statistics",
            chunk_numbers,
            flow_params[param],
            ["Number of chunks", _get_ylabel(param)],
            legend_string=legend_string,
        )

        filename = f"{stats_type.lower()}_{param}_{server_node}_to_{node}.png"
        Pack.dump_plot("mpeg_dash", filename, fig)
        plt.close(fig)
    return 0


@handle_keyboard_interrupt
def plot_mpeg_dash(parsed_data):
    """
    Plot statistics obtained from MPEG-DASH

    Parameters
    ----------
    parsed_data : Dict
        JSON data parsed from MPEG-DASH application
    """

    for node in parsed_data:
        node_data = parsed_data[node]
        for connection in node_data:
            for server_ip in connection:
                flow_data = connection[server_ip]
                video_stats = flow_data["video"]
                try:
                    _plot_mpeg_dash(video_stats, node, server_ip, "Video")
                except (KeyError, TypeError, ValueError, RuntimeError, IOError) as excp:
                    logger.error(
                        "Error generating plots for video statistics: %s",
                        excp,
                        exc_info=True,
                    )

                if flow_data["audio"][0]["audio_enabled"] is True:
                    audio_stats = flow_data["audio"]
                    try:
                        _plot_mpeg_dash(audio_stats, node, server_ip, "Audio")
                    except (
                        KeyError,
                        TypeError,
                        ValueError,
                        RuntimeError,
                        IOError,
                    ) as excp:
                        logger.error(
                            "Error generating plots for audio statistics: %s",
                            excp,
                            exc_info=True,
                        )
