# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Plot ss results"""

import matplotlib.pyplot as plt

from ..pack import Pack
from .common import simple_plot, mix_plot


def _get_list_of_ss_params():
    """
    Return list of params parsed by ss
    """
    return ['cwnd', 'rtt', 'dev_rtt', 'ssthresh', 'rto', 'delivery_rate']


def _extract_from_ss_flow(flow, node, dest_ip, dest_port):
    """
    Extract information from flow data and convert it to
    conviniently plottable data format

    Parameters
    ----------
    flow : List
        List with timestamps and stats
    node : string
        Node from which ss results were obtained from
    dest_ip : string
        Destination ip address of the flow
    dest_port : string
        Destination port of the flow

    Returns
    -------
    (timestamp, flow_params)
        Return timestamp and flow parameters
    """
    if len(flow) == 0:
        raise ValueError('Flow from {} to destination {}:{}'
                         'doesn\'t have any parsed ss result.'.format(node,
                                                                      dest_ip, dest_port))

    start_time = float(flow[0]['timestamp'])

    timestamp = []
    flow_params = {}

    for param in _get_list_of_ss_params():
        flow_params[param] = []

    for data in flow:
        for stat in flow_params:
            if stat in data:
                flow_params[stat].append(float(data[stat]))
            else:
                flow_params[stat].append(None)
        relative_time = float(data['timestamp']) - start_time
        timestamp.append(relative_time)

    return (timestamp, flow_params)


def _plot_ss_flow(flow, node, dest_ip, dest_port):
    """
    Plot ss stats of the flow

    Parameters
    ----------
    exp_name : string
        Name of experiment for which results were obtained
    flow : List
        List with timestamps and stats
    node : string
        Node from which ss results were obtained from
    dest_ip : string
        Destination ip address of the flow
    dest_port : string
        Destination port of the flow
    """
    (timestamp, flow_params) = _extract_from_ss_flow(
        flow, node, dest_ip, dest_port)
    for param in flow_params:
        # Plot the values
        title = 'ss: {dest_ip}:{dest_port}'.format(
            dest_ip=dest_ip, dest_port=dest_port)
        fig = simple_plot(title, timestamp,
                          flow_params[param], 'Time(s)', param)
        filename = f'{node}_{dest_ip}:{dest_port}_{param}.png'
        Pack.dump_plot('ss', filename, fig)
        plt.close(fig)

    return (timestamp, flow_params)

# pylint: disable=too-many-locals
def plot_ss(parsed_data):
    """
    Plot statistics obtained from ss

    Parameters
    ----------
    exp_name : string
        Name of experiment for which results were obtained
    parsed_data : Dict
        JSON data parsed from ss
    """

    # pylint: disable=too-many-nested-blocks
    for node in parsed_data:
        node_data = parsed_data[node]
        for connection in node_data:
            for dest_ip in connection:

                all_flow_data = []

                flow_data = connection[dest_ip]
                for dest_port in flow_data:
                    flow = flow_data[dest_port]
                    values = _plot_ss_flow(flow, node, dest_ip, dest_port)
                    all_flow_data.append(
                        {'values': values, 'label': '{}:{}'.format(dest_ip, dest_port)})

                if len(all_flow_data) > 0:

                    x_vals = []
                    labels = []

                    for flow_data in all_flow_data:
                        x_vals.append(flow_data['values'][0])
                        labels.append(flow_data['label'])

                    for param in all_flow_data[0]['values'][1]:
                        y_vals = []
                        for flow_data in all_flow_data:
                            y_vals.append(flow_data['values'][1][param])

                        data = []

                        for i in range(len(labels)):
                            data.append(
                                {'values': (x_vals[i], y_vals[i]), 'label': labels[i]})

                        fig = mix_plot('ss: ' + param, data, 'Time(s)', param)
                        filename = f'mix_{node}_{dest_ip}_{param}.png'
                        Pack.dump_plot('ss', filename, fig)
                        plt.close(fig)
