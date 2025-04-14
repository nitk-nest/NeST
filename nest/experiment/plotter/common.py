# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""Common plotting logic among tools"""

import random
import os
import numpy as np
import matplotlib.pyplot as plt
from nest.engine.gnuplot import build_gnuplot
from ..pack import Pack


def simple_plot(title, x_list, y_list, labels, legend_string=None):
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
    labels : list
        Labels for the axes, specified as [x_label, y_label]

    legend_string : None/str
        If a string, then have a legend in the plot

    Returns
    -------
    matplotlib.plt.fig
        fig of plot
    """
    fig = plt.figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.plot(x_list, y_list)
    axis.set_xlabel(labels[0])
    axis.set_ylabel(labels[1])
    axis.set_title(title)

    if legend_string is not None:
        axis.legend([legend_string], loc="best")

    return fig


def mix_plot(title, data, labels, with_sum=False):
    """Plot multiple sets of values and their total sum

    Parameters
    ----------
    title : str
        Title for the plot
    data : List
        list of values
    labels : list
        Labels for the axes, specified as [x_label, y_label]
    with_sum : boolean
        If should plot the sum of all y values (Default value = False)

    Returns
    -------
    maplotlib.plt.fig
        fig of plot
    """
    fig, axis = plt.subplots()

    for chunk in data:
        (x_list, y_list) = chunk["values"]
        label = chunk["label"]
        axis.plot(x_list, y_list, label=label)

    if with_sum:

        x_values = []
        for chunk in data:
            (x_list, _) = chunk["values"]
            x_values.append(x_list)

        # Get sorted list of all x values
        x_values = np.unique(np.concatenate(x_values))

        total = np.array([0.0] * len(x_values))
        for chunk in data:
            (x_list, y_list) = chunk["values"]
            # Interpolate y values on the combined x values
            y_value = np.interp(x_values, x_list, y_list, left=0, right=0)
            total += y_value

        axis.plot(x_values, total, label="Aggregate", alpha=0.5)

    axis.set_xlabel(labels[0])
    axis.set_ylabel(labels[1])
    axis.set_title(title)
    axis.legend(loc="best")

    return fig


def bar_plot(title, x_list, y_list, labels, legend_string=None):
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
    labels : list
       Labels for the axes, specified as [x_label, y_label]
    legend_string : None/str
        If a string, then have a legend in the plot

    Returns
    -------
    matplotlib.plt.fig
        fig of plot
    """
    fig = plt.figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.bar(x_list, y_list, width=0.3)
    axis.set_xlabel(labels[0])
    axis.set_ylabel(labels[1])
    axis.set_title(title)

    if legend_string is not None:
        axis.legend([legend_string])

    return fig


def html_table(row_labels, col_labels, table_data):
    """
    Table values

    Parameters
    ----------
    rowLables : str
        Labels for the rows of the table
    colLables : List
        Labels for the columns of the table
    table_data : List
        Data to be filled in the table

    Returns
    -------
    HTML markup for table using provided
    labels and data.
    """
    table_html = "<html><table><caption>Comparison Plot</caption><tr><td></td>"
    for col_label in col_labels:
        table_html += f"<th>{col_label}</th>"
    table_html += "</tr>"
    for row_index in range(len(row_labels)):
        table_html += "<tr>"
        table_html += f"<th>{row_labels[row_index]}</th>"
        for col_index in range(len(col_labels)):
            table_html += f"<td>{table_data[row_index][col_index]}</td>"
        table_html += "</tr>"
    table_html += "</table></html>"
    return table_html


def simple_gnu_plot(paths, labels, legend, title=""):
    """Plot Gnuplot

    Parameters
    ----------
    paths : Dict[str, str]
    Dictionary containing file paths with keys 'dat', 'plt', and 'eps'
    labels : list
       Labels for the axes, specified as [x_label, y_label]
    legend: str
        Legend in the plot
    title : str
        Title for the plot
    """
    directory = os.getcwd() + "/"
    pltline = (
        f"set term postscript eps enhanced color blacktext 'Arial'\n"
        f"set output '{directory}{paths['eps']}'\n"
        f"set title '{title}'\n"
        f"set xlabel '{labels[0]}'\n"
        f"set ylabel '{labels[1]}'\n"
        f"set key right top vertical\n"
        f"stats '{directory}{paths['dat']}' using 2 prefix 'Y' nooutput\n"
        f"set autoscale y\n"
        f"if (Y_min == Y_max) set yrange [Y_min-1:Y_max+1]\n"
        f"plot '{directory}{paths['dat']}' "
        f"title '{legend}' "
        "with lines smooth csplines "
        "lw 1.5 lc rgb 'red'\n"
    )

    build_gnuplot(directory, paths["plt"], pltline)
    Pack.set_owner(paths["plt"])
    Pack.set_owner(paths["eps"])


def mix_gnu_plot(dat_list, paths, labels, legend_list, title=""):
    """Plot Gnuplot

    Parameters
    ----------
    dat_list : List[str]
        List of paths to .dat files containing the datasets to plot.
    paths : Dict[str, str]
        Dictionary containing file paths with keys 'plt' and 'eps'.
    labels : list
       Labels for the axes, specified as [x_label, y_label]
    legend_list: List
        List of legends in the plot
    title : str
        Title for the plot
    """
    if not dat_list or not legend_list or len(dat_list) != len(legend_list):
        raise ValueError(
            "dat_list and legend_list must be non-empty and of equal length."
        )

    directory = os.getcwd() + "/"

    pltline = (
        "set term postscript eps enhanced color blacktext 'Arial'\n"
        f"set output '{directory}{paths['eps']}'\n"
        f"set title '{title}'\n"
        f"set xlabel '{labels[0]}'\n"
        f"set ylabel '{labels[1]}'\n"
        "set key right top vertical\n"
    )

    pltline += (
        f"stats '{directory}{dat_list[0]}' using 2 nooutput\n"
        "set autoscale y\n"
        "if (STATS_min_y == STATS_max_y) set yrange [STATS_min_y-1:STATS_max_y+1]\n"
        "if (STATS_records == 0) set yrange [-1:1]\n"
    )

    # Generate high-contrast colors
    color_ratio = 0.61803398875
    hue = random.random()
    colors = []
    for _ in range(len(dat_list)):
        hue += color_ratio
        hue %= 1
        # For better color generation of RGB:
        # red  : int(255 * (1 - hue))
        # green: int(255 * hue)
        # blue : int(255 * (hue**0.5))

        colors.append(
            f"rgb({int(255 * (1 - hue))},{int(255 * hue)},{int(255 * (hue**0.5))})"
        )

    splot = "plot "
    for datfile, legend, color in zip(dat_list, legend_list, colors):
        splot += (
            f'"{directory}{datfile}" '
            f'title "{legend}" '
            "with lines smooth csplines "
            f"lw 1.5 lc {color}, "
        )

    pltline += splot.rstrip(", ") + "\n"

    build_gnuplot(directory, paths["plt"], pltline)
    Pack.set_owner(paths["plt"])
    Pack.set_owner(paths["eps"])
