# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import matplotlib.pyplot as plt

from .common import simple_plot
from ..pack import Pack


def _extract_from_tc_stats(stats, node, interface):
    """
    Extract information from tc stats and convert it to 
    conviniently plottable data format
    
    :param stats: List of timestamps and stats
    :type stats: List
    :param node: Node from which tc results were obtained from
    :type node: string
    :param interface: Interface from which results were obtained from
    :type interface: string
    """

    if len(stats) == 0:
        raise ValueError('qdisc at {} of {} doesn\'t have any'
                         'parsed tc result.'.format(interface, node))

    qdisc = stats[0]['kind']
    start_time = float(stats[0]['timestamp'])

    timestamp = []
    stats_params = {}

    for param in stats[0]:
        if param != 'timestamp' and param != 'kind':
            stats_params[param] = []

    for data in stats:
        for param in stats_params:
            stats_params[param].append(data[param])
        relative_time = float(data['timestamp']) - start_time
        timestamp.append(relative_time)

    return (qdisc, timestamp, stats_params)


def _plot_tc_stats(exp_name, stats, node, interface):
    """
    Plot tc stats of the flow
    
    :param exp_name: Name of experiment for which results were obtained
    :type exp_name: string
    :param stats: List with timestamps and stats
    :type stats: List
    :param node: Node from which tc results were obtained from
    :type node: string
    :param interface: Interface from which results were obtained from
    :type interface: string
    """

    (qdisc, timestamp, stats_params) = _extract_from_tc_stats(stats, node, interface)
    for param in stats_params:
        title = 'tc: {node}:{qdisc}'.format(node=node, qdisc=qdisc)
        fig = simple_plot(title, timestamp,
                          stats_params[param], 'Time(s)', param)
        filename = '{node}_{interface}_{qdisc}_{param}.png'.format(node=node,
                                                                   interface=interface, qdisc=qdisc, param=param)
        Pack.dump_plot('tc', filename, fig)
        plt.close(fig)


def plot_tc(exp_name, parsed_data):
    """
    Plot statistics obtained from tc

    :param exp_name: Name of experiment for which results were obtained
    :type exp_name: string
    :param parsed_data: JSON data parsed from ss
    :type parsed_data: Dict
    """

    for node in parsed_data:
        node_data = parsed_data[node]
        for interfaces in node_data:
            for interface in interfaces:
                qdisc = interfaces[interface]
                for handle in qdisc:
                    stats = qdisc[handle]
                    _plot_tc_stats(exp_name, stats, node, interface)
