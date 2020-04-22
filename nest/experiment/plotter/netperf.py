# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import matplotlib.pyplot as plt

from ..pack import Pack
from .common import simple_plot, mix_plot

def _plot_netperf_flow(exp_name, flow, node, dest):
    """
    Plot netperf stats of the flow
    
    :param exp_name: Name of experiment for which results were obtained
    :type exp_name: string
    :param flow: List with timestamps and stats
    :type flow: List
    :param node: Node from which netperf results were obtained from
    :type node: string
    :param dest: Destination ip:port address of the flow
    :type dest_ip: string
    """

    if len(flow) == 0:
        raise ValueError('Flow from {} to destination {}' \
                'doesn\'t have any parsed ss result.'.format(node, 
                dest))

    start_time = float(flow[0]['timestamp'])
    
    timestamp = []
    throughput = []

    for data in flow:
        throughput.append(float(data['throughput'])) 
        relative_time = float(data['timestamp']) - start_time
        timestamp.append(relative_time)
    
    title = 'netperf: {dest}'.format(dest = dest)
    fig = simple_plot(title, timestamp, throughput, 'Time(s)', 'throughput')
    filename = '{node}_{dest}_throughput.png'.format(node = node,
        dest = dest)
    Pack.dump_plot('netperf', filename, fig)
    plt.close(fig)

    return (timestamp, throughput)

def plot_netperf(exp_name, parsed_data):
    """
    Plot statistics obtained from netperf

    :param exp_name: Name of experiment for which results were obtained
    :type exp_name: string
    :param parsed_data: JSON data parsed from ss
    :type parsed_data: Dict
    """

    for node in parsed_data:
        node_data = parsed_data[node]

        all_flow_data = []
        for connection in node_data:
            for dest in connection:
                flow = connection[dest]
                values = _plot_netperf_flow(exp_name, flow, node, dest)
                all_flow_data.append({'label': dest, 'values': values})

        fig = mix_plot('netperf', all_flow_data, 'Time(s)', 'throughput', with_sum = True)
        filename = 'mix_{node}_throughput.png'.format(node = node, dest = dest)
        Pack.dump_plot('netperf', filename, fig)
        plt.close(fig)
