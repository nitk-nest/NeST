# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import matplotlib.pyplot as plt

def plot(x, y, xlabel='', ylabel=''):
    """
    An utility function to plot

    :param x: values to be plotted on x-axis
    :type x: list of ints
    :param y: values to be plotted on y-axis
    :type x: list of ints
    :param xlabel: x-axis label
    :type xlabel: string
    :param ylabel: y-axis label
    :type ylabel: string
    """
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.plot(x, y)
    plt.show()