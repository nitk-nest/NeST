# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import matplotlib.pyplot as plt
import math
import numpy as np

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


def sub_plots(x, y, xlabel='', ylabel=[]):
    """

    An utility function to plot subplots

    :param x: values to plotted on the x-axis 
    :type x: list of ints
    :param y: values to be plotted on y-axis
    :type x: numpy 2-D array of floats
    :param xlabel: x-axis labels
    :type xlabel: list of strings
    :param ylabel: y-axis labels
    :type ylabel: list of strings
    """

    # calculate the dimension of the subplot
    n = math.ceil(math.sqrt(y.shape[0]))

    # TODO: display only required plots    
    fig, a = plt.subplots(n ,n)

    # if only one paramter is to be plotted
    if y.shape[0] == 1:
        a.plot(x, y[0, :])
        a.set_title(ylabel[0])
        plt.show()
        return

    param_index = 0
    for i in range(n):
        for j in range(n):
            if param_index >= y.shape[0]:
                plt.show()
                return 
            a[i][j].plot(x, y[param_index, :])
            a[i][j].set_title(ylabel[param_index])
            param_index = param_index + 1
    
    plt.show()
