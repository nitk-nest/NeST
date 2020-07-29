# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Common plotting logic among tools"""

import numpy as np
import matplotlib.pyplot as plt

#pylint: disable=invalid-name

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


def mix_plot(title, data, x_label, y_label, with_sum=False):
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
        ax.plot(x_list, y_list, label=label)

    if with_sum:

        x = []
        for chunk in data:
            (x_list, _) = chunk['values']
            x.append(x_list)

        # Get sorted list of all x values
        x = np.unique(np.concatenate(x))

        total = np.array([0.0]*len(x))
        for chunk in data:
            (x_list, y_list) = chunk['values']
            # Interpolate y values on the combined x values
            y = np.interp(x, x_list, y_list, left=0, right=0)
            total += y

        ax.plot(x, total, label='sum')

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend()

    return fig
