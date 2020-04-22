# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import matplotlib.pyplot as plt
from itertools import zip_longest

def simple_plot(title, x_list, y_list, x_label, y_label):
    """
    Plot values

    :param title: Title for the plot
    :type title: string
    :param x_list: List of x values
    :type x_list: List
    :param y_list: List of y values
    :type y_list: List
    :param x_label: Label for x values
    :type x_label: string
    :param y_label: Label for y values
    :type y_label: string
    :return: fig of plot
    :r_type: maplotlib.plt.fig
    """

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(x_list, y_list)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    return fig

def mix_plot(title, data, x_label, y_label, with_sum = False):
    """
    Plot multiple sets of values and their total sum

    :param title: Title for the plot
    :type title: string
    :param data: list of values
    :type data: List
    :param x_label: Label for x values
    :type x_label: string
    :param y_label: Label for y values
    :type y_label: string
    :param with_sum: If should plot the sum of all y values
    :type with_sum: boolean
    :return: fig of plot
    :r_type: maplotlib.plt.fig
    """

    fig, ax = plt.subplots()
    # TODO: I couldn't think of better variable name :(
    for chunk in data:
        (x_list, y_list) = chunk['values']
        label = chunk['label']
        ax.plot(x_list, y_list, label = label)

    if with_sum:
        sum = []
        ox_list = []
        for chunk in data:
            (x_list, y_list) = chunk['values']
            if sum == []:
                sum = y_list
                ox_list = x_list
            else:
                sum = [x+y for x,y in zip_longest(sum, y_list, fillvalue=0)]
                if len(x_list) > len(ox_list):
                    ox_list = x_list

        ax.plot(ox_list, sum, label = 'sum')
            

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend()

    return fig
