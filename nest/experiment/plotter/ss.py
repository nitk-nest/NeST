# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import matplotlib.pyplot as plt
import matplotlib.style as style

def _set_plot_theme():
    """
    The matplotlib plot theme
    """

    style.use('seaborn-paper')
    style.use('ggplot')

def _get_list_of_ss_params():
    """
    Return list of params parsed by ss
    """

    return ['cwnd', 'rtt', 'dev_rtt', 'ssthresh', 'rto', 'delivery_rate']

def _extract_from_ss_flow(flow, node, dest_ip, dest_port):
    """
    Extract information from flow data and convert it to
    conviniently plottable data format

    :param flow: List with timestamps and stats
    :type flow: List
    :param node: Node from which ss results were obtained from
    :type node: string
    :param dest_ip: Destination ip address of the flow
    :type dest_ip: string
    :param dest_port: Destination port of the flow
    :type dest_port: string
    :return: Return timestamp and flow parameters
    :r_type: (timestamp, flow_params)
    """

    if len(flow) == 0:
        raise ValueError('Flow from {} to destination {}:{} \
                doesn\'t have any parsed ss result.')

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

def _plot_ss_flow(exp_name, flow, node, dest_ip, dest_port):
    """
    Plot ss stats of the flow
    
    :param exp_name: Name of experiment for which results were obtained
    :type exp_name: string
    :param flow: List with timestamps and stats
    :type flow: List
    :param node: Node from which ss results were obtained from
    :type node: string
    :param dest_ip: Destination ip address of the flow
    :type dest_ip: string
    :param dest_port: Destination port of the flow
    :type dest_port: string
    """

    (timestamp, flow_params) = _extract_from_ss_flow(flow, node, dest_ip, dest_port)
    for param in flow_params:
        # Plot the values
        fig = plt.figure()
        fig.suptitle('ss: {dest_ip}:{dest_port}'.format(dest_ip = dest_ip, dest_port = dest_port))
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(timestamp, flow_params[param],)
        ax.set_xlabel('Time(s)')
        ax.set_ylabel(param)

        fig.savefig('ss_{exp_name}_{node}_{param}_{dest_ip}:{dest_port}.png'.format(exp_name = exp_name, 
            node = node, param = param, dest_ip = dest_ip, dest_port = dest_port))
        plt.close(fig)

def plot_ss(exp_name, parsed_data):
    """
    Plot statistics obtained from ss

    :param exp_name: Name of experiment for which results were obtained
    :type exp_name: string
    :param parsed_data: JSON data parsed from ss
    :type parsed_data: Dict
    """

    _set_plot_theme()

    for node in parsed_data:
        node_data = parsed_data[node]
        for connection in node_data:
            for dest_ip in connection:
                flow_data = connection[dest_ip]
                for dest_port in flow_data:             
                    flow = flow_data[dest_port]
                    _plot_ss_flow(exp_name, flow, node, dest_ip, dest_port)

