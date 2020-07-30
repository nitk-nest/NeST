# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Plot ping results"""

import matplotlib.pyplot as plt

from ..pack import Pack
from .common import simple_plot


def _plot_ping_flow(flow, node, dest):
    """
    Plot ping stats of the flow

    Parameters
    ----------
    exp_name : str
        Name of experiment for which results were obtained
    flow : List
        List with timestamps and stats
    node : str
        Node from which ping results were obtained from
    dest :
        Destination ip:port address of the flow

    Returns
    -------
    tuple
        Timestamped throughput values
    """
    if len(flow) == 0:
        raise ValueError('Flow from {} to destination {}'
                         'doesn\'t have any parsed ping result.'.format(node,
                                                                        dest))

    start_time = float(flow[0]['timestamp'])

    timestamp = []
    throughput = []

    for data in flow:
        throughput.append(float(data['rtt']))
        relative_time = float(data['timestamp']) - start_time
        timestamp.append(relative_time)

    title = 'ping: {dest}'.format(dest=dest)
    fig = simple_plot(title, timestamp, throughput, 'Time(s)', 'ping')
    filename = '{node}_{dest}_ping.png'.format(node=node,
                                               dest=dest)
    Pack.dump_plot('ping', filename, fig)
    plt.close(fig)

    return (timestamp, throughput)


def plot_ping(parsed_data):
    """
    Plot statistics obtained from ping

    Parameters
    ----------
    exp_name : str
        Name of experiment for which results were obtained
    parsed_data : Dict
        JSON data parsed from ss
    """
    for node in parsed_data:
        node_data = parsed_data[node]

        # all_flow_data = []
        for connection in node_data:
            for dest in connection:
                flow = connection[dest]
                _plot_ping_flow(flow, node, dest)
