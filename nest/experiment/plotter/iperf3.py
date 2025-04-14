# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""Plot ss results"""

import logging
import pandas as pd
import matplotlib.pyplot as plt
from nest import config
from nest.experiment.interrupts import handle_keyboard_interrupt
from ..pack import Pack
from .common import simple_plot, simple_gnu_plot

logger = logging.getLogger(__name__)


def _extract_from_iperf3_flow(flow, node, dest_ip, local_port):
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
    local_port : string
        Local port of the flow

    Returns
    -------
    (timestamp, sending_rate) or None
        Return timestamp and sending rate
    """
    # "meta" item will always be present, hence `<= 1`
    if len(flow) <= 1:
        logger.warning(
            "Flow from %s and port %s to destination ip %s doesn't have any parsed ss result.",
            node,
            dest_ip,
            local_port,
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
        # add relative time to timestamp
        timestamp.append(float(data["timestamp"]) - start_time)

    return {"destination_node": destination_node, "values": (timestamp, sending_rate)}


def _plot_iperf3_flow(flow, node, dest_ip, local_port):
    """
    Plot iperf3 stats of the flow

    Parameters
    ----------
    exp_name : str
        Name of experiment for which results were obtained
    flow : List
        List with timestamps and stats
    node : str
        Node from which iperf3 results were obtained from
    dest_ip : str
        Destination ip address of the flow
    local_port : str
        Local port of the flow
    """
    data = _extract_from_iperf3_flow(flow, node, dest_ip, local_port)
    destination_node = data["destination_node"]
    values = data["values"]

    if values is None:
        return
    (timestamp, sending_rate) = values

    legend_string = f"{node} from port {local_port} to {destination_node} ({dest_ip})"

    fig = simple_plot(
        "",
        timestamp,
        sending_rate,
        ["Time (Seconds)", "Sending Rate (Mbps)"],
        legend_string,
    )

    base_filename = (
        f"sending_rate_{node}({local_port})_to_{destination_node}({dest_ip})"
    )
    Pack.dump_plot("iperf3", f"{base_filename}.png", fig)
    plt.close(fig)
    if config.get_value("enable_gnuplot"):
        data_frame = pd.DataFrame(list(zip(timestamp, sending_rate)))
        Pack.dump_datfile("iperf3", f"{base_filename}.dat", data_frame)

        # Store paths in a dict for .dat, .eps and .plt
        paths = {
            "dat": Pack.get_path("iperf3", f"{base_filename}.dat"),
            "eps": Pack.get_path("iperf3", f"{base_filename}.eps"),
            "plt": Pack.get_path("iperf3", f"{base_filename}.plt"),
        }

        simple_gnu_plot(
            paths,
            ["Time (Seconds)", "Sending Rate (Mbps)"],
            legend_string,
        )


@handle_keyboard_interrupt
def plot_iperf3(parsed_data):
    """
    Plot statistics obtained from iperf3

    Parameters
    ----------
    exp_name : string
        Name of experiment for which results were obtained
    parsed_data : Dict
        JSON data parsed from iperf3
    """

    for node in parsed_data:
        node_data = parsed_data[node]
        for connection in node_data:
            for dest_ip in connection:
                flow_data = connection[dest_ip]
                for local_port in flow_data:
                    flow = flow_data[local_port]
                    _plot_iperf3_flow(flow, node, dest_ip, local_port)
