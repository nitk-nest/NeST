# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""Common plotting logic among tools"""

import random
import os
import numpy as np
import matplotlib.pyplot as plt
from ..pack import Pack

# pylint: disable=invalid-name

# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
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
        ax.legend([legend_string], loc="best")

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
    ax.legend(loc="best")

    return fig

def bar_plot(title, x_list, y_list, x_label, y_label, legend_string=None):
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
    ax.bar(x_list, y_list, width=0.3)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    if legend_string is not None:
        ax.legend([legend_string])

    return fig


def html_table(rowLabels, colLabels, tableData):
    """
    Table values

    Parameters
    ----------
    rowLables : str
        Labels for the rows of the table
    colLables : List
        Labels for the columns of the table
    tableData : List
        Data to be filled in the table

    Returns
    -------
    HTML markup for table using provided
    labels and data.
    """
    table_html = "<html><table><caption>Comparison Plot</caption><tr><td></td>"
    for colLabel in colLabels:
        table_html += f"<th>{colLabel}</th>"
    table_html += "</tr>"
    for row_index in range(len(rowLabels)):
        table_html += "<tr>"
        table_html += f"<th>{rowLabels[row_index]}</th>"
        for col_index in range(len(colLabels)):
            table_html += f"<td>{tableData[row_index][col_index]}</td>"
        table_html += "</tr>"
    table_html += "</table></html>"
    return table_html


def simple_gnu_plot(path_dat, path_plt, path_eps, x_label, y_label, legend, title=""):
    """Plot Gnuplot

    Parameters
    ----------
    path_dat : str
        Path of dat file
    path_plt : str
        Path of plt file
    path_eps : str
        path of eps file
    x_label : str
        Label for x values
    y_label : str
        Label for y values
    legend: str
        Legend in the plot
    title : str
        Title for the plot
    """
    directory = os.getcwd() + "/"
    pltline = (
        f"set term postscript eps  color blacktext 'Arial'\n"
        f'set output "{directory}{path_eps}"\n'
        f"set title '{title}'\n"
        f'set xlabel "{x_label}"\n'
        f'set ylabel "{y_label}"\n'
        f"set key right top vertical\n"
    )
    splot = (
        "plot"
        + '"'
        + directory
        + path_dat
        + '"'
        + "title "
        + '"'
        + legend
        + '"'
        + " with lines lw 0.5 lc 'blue'"
    )
    pltline += splot

    # TODO: This code should be moved to engine module
    run_cmd = "gnuplot " + "'" + directory + path_plt + "'"
    with open(path_plt, "w") as pltfile:
        pltfile.write(pltline)
        pltfile.close()
    os.system(run_cmd)
    Pack.set_owner(path_plt)
    Pack.set_owner(path_eps)


def mix_gnu_plot(dat_list, path_plt, path_eps, x_label, y_label, legend_list, title=""):
    """Plot Gnuplot

    Parameters
    ----------
    dat_list : List
        List of dat file's paths
    path_plt : str
        Path of plt file
    path_eps : str
        path of eps file
    x_label : str
        Label for x values
    y_label : str
        Label for y values
    legend_list: List
        List of legends in the plot
    title : str
        Title for the plot
    """
    directory = os.getcwd() + "/"
    pltline = "set term postscript eps  color blacktext 'Arial'\n"
    pltline += "set output " + '"' + directory + path_eps + '"' + "\n"
    pltline += "set title " + "'" + title + "'" + "\n"
    pltline += "set xlabel " + '"' + x_label + '"' + "\n"
    pltline += "set ylabel " + '"' + y_label + '"' + "\n"
    pltline += "set key right top vertical" + "\n"
    splot = "plot "
    for datfile, legend_string in zip(dat_list, legend_list):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        c = random.randint(0, 255)
        color = "rgb(" + str(a) + "," + str(b) + "," + str(c) + ")"
        splot += (
            '"'
            + directory
            + datfile
            + '"'
            + " title "
            + '"'
            + legend_string
            + '"'
            + " with lines lw 0.5 lc "
            + color
            + ","
        )
    splot = splot[:-1]
    pltline += splot
    run_cmd = "gnuplot " + "'" + directory + path_plt + "'"
    with open(path_plt, "w") as pltfile:
        pltfile.write(pltline)
        pltfile.close()
    os.system(run_cmd)
    Pack.set_owner(path_plt)
    Pack.set_owner(path_eps)
