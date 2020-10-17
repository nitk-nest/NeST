# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Plot netperf results"""

import matplotlib.pyplot as plt

from ..pack import Pack
from .common import simple_plot, mix_plot


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
    tuple
        Timestamped throughput values
    """
    # "meta" item will always be present, hence `<= 1`
    if len(flow) <= 1:
        raise ValueError('Flow from {} to destination {}'
                         'doesn\'t have any parsed ss result.'.format(node,
                                                                      dest))

    # First item is the "meta" item with user given information
    user_given_start_time = float(flow[0]['start_time'])

    # "Bias" actual start_time in experiment with user given start time
    start_time = float(flow[1]['timestamp']) - user_given_start_time

    timestamp = []
    throughput = []

    for data in flow[1:]:
        throughput.append(float(data['throughput']))
        relative_time = float(data['timestamp']) - start_time
        timestamp.append(relative_time)

    title = 'netperf: {dest}'.format(dest=dest)
    fig = simple_plot(title, timestamp, throughput, 'Time(s)', 'throughput')
    filename = '{node}_{dest}_throughput.png'.format(node=node, dest=dest)
    Pack.dump_plot('netperf', filename, fig)
    plt.close(fig)

    return (timestamp, throughput)


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
                all_flow_data.append({'label': dest, 'values': values})

        fig = mix_plot('netperf', all_flow_data, 'Time(s)',
                       'throughput', with_sum=True)
        filename = f'mix_{node}_throughput.png'
        Pack.dump_plot('netperf', filename, fig)
        plt.close(fig)
