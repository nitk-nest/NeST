# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import matplotlib.pyplot as plt

def simple_plot(title, x_list, y_list, x_label, y_label):
    """

    """

    fig = plt.figure()
    fig.suptitle(title)
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(x_list, y_list)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    return fig

