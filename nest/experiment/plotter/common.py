# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Common plotting logic among tools"""

import numpy as np
import matplotlib.pyplot as plt

# pylint: disable=invalid-name

# pylint: disable=too-many-arguments
def simple_plot(title, x_list, y_list, x_label, y_label, legend_string=None):
    """
    Plot values

    Parameters
    ----------
    title : str
        Title for the plot
    x_list : List
        List of x values
    y_list : List
        List of y values
    x_label : str
        Label for x values
    y_label : str
        Label for y values
    legend_string : None/str
        If a string, then have a legend in the plot

    Returns
    -------
    matplotlib.plt.fig
        fig of plot
    """
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(x_list, y_list)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    if legend_string is not None:
        ax.legend([legend_string])

    return fig


def mix_plot(title, data, x_label, y_label, with_sum=False):
    """Plot multiple sets of values and their total sum

    Parameters
    ----------
    title : str
        Title for the plot
    data : List
        list of values
    x_label : str
        Label for x values
    y_label : str
        Label for y values
    with_sum : boolean
        If should plot the sum of all y values (Default value = False)

    Returns
    -------
    maplotlib.plt.fig
        fig of plot
    """
    fig, ax = plt.subplots()
    # TODO: I couldn't think of better variable name :(
    for chunk in data:
        (x_list, y_list) = chunk["values"]
        label = chunk["label"]
        ax.plot(x_list, y_list, label=label)

    if with_sum:

        x = []
        for chunk in data:
            (x_list, _) = chunk["values"]
            x.append(x_list)

        # Get sorted list of all x values
        x = np.unique(np.concatenate(x))

        total = np.array([0.0] * len(x))
        for chunk in data:
            (x_list, y_list) = chunk["values"]
            # Interpolate y values on the combined x values
            y = np.interp(x, x_list, y_list, left=0, right=0)
            total += y

        ax.plot(x, total, label="Aggregate", alpha=0.5)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.legend()

    return fig
