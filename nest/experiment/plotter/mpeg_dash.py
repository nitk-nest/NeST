# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2024 NITK Surathkal

"""Plot MPEG-DASH results"""

import logging
import matplotlib.pyplot as plt
from nest.experiment.interrupts import handle_keyboard_interrupt
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


def _extract_from_mpeg_dash(flow, node, server_ip):
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

    Returns
    -------
    flow_params or None
        Return flow parameters
    """
    # "meta" item will always be present, hence `<= 1`
    if len(flow) <= 1:
        logger.warning(
            "MPEG-DASH application from server %s to  client %s doesn't have any parsed result.",
            server_ip,
            node,
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
    data = _extract_from_mpeg_dash(flow, node, server_ip)

    server_node = data["server_node"]
    if data["values"] is None:
        return None
    (chunk_numbers, flow_params) = data["values"]

    legend_string = f"Server {server_node} to client {node}"
    for param in flow_params:
        fig = simple_plot(
            f"MPEG-DASH {stats_type} Statistics",
            chunk_numbers,
            flow_params[param],
            "Number of chunks",
            _get_ylabel(param),
            legend_string=legend_string,
        )

        filename = f"{stats_type.lower()}_{param}_{server_node}_to_{node}.png"
        Pack.dump_plot("mpeg_dash", filename, fig)
        plt.close(fig)


# pylint: disable=too-many-locals
@handle_keyboard_interrupt
def plot_mpeg_dash(parsed_data):
    """
    Plot statistics obtained from MPEG-DASH

    Parameters
    ----------
    parsed_data : Dict
        JSON data parsed from MPEG-DASH application
    """

    # pylint: disable=too-many-nested-blocks
    for node in parsed_data:
        node_data = parsed_data[node]
        for connection in node_data:
            for server_ip in connection:
                flow_data = connection[server_ip]

                video_stats = flow_data["video"]
                audio_stats = flow_data["audio"]
                video_stats_summary = flow_data["video_summary"]
                audio_stats_summary = flow_data["audio_summary"]

                log_string = "### Video Stream Information ### \n"
                log_string += "\t Number of bitrate switches: "
                log_string += f"{video_stats_summary['number_of_bitrate_switches']} \n"
                log_string += "\t Average Bitrate: "
                log_string += f"{video_stats_summary['average_bitrate']:.2f} Kbps \n"
                log_string += "\t Average Throughput: "
                log_string += f"{video_stats_summary['average_throughput']:.2f} Kbps \n"
                log_string += "\t Average Buffer: "
                log_string += f"{video_stats_summary['average_buffer']:.2f} ms \n"
                log_string += "\t Average RTT: "
                log_string += f"{video_stats_summary['average_rtt']:.2f} s \n\n"

                log_string += "\t ### Audio Stream Information ### \n"
                log_string += "\t Number of bitrate switches: "
                log_string += f"{audio_stats_summary['number_of_bitrate_switches']} \n"
                log_string += "\t Average Bitrate: "
                log_string += f"{audio_stats_summary['average_bitrate']:.2f} Kbps \n"
                log_string += "\t Average Throughput: "
                log_string += f"{audio_stats_summary['average_throughput']:.2f} Kbps \n"
                log_string += "\t Average Buffer: "
                log_string += f"{audio_stats_summary['average_buffer']:.2f} ms \n"
                log_string += "\t Average RTT: "
                log_string += f"{audio_stats_summary['average_rtt']:.2f} s \n"

                logger.info(log_string)
                try:
                    _plot_mpeg_dash(video_stats, node, server_ip, "Video")
                except TypeError:
                    logger.error(
                        "Error generating plots for video statistics. "
                        "No statistics have been received!"
                    )

                try:
                    _plot_mpeg_dash(audio_stats, node, server_ip, "Audio")
                except TypeError:
                    logger.error(
                        "Error generating plots for audio statistics. "
                        "No statistics have been received!"
                    )
