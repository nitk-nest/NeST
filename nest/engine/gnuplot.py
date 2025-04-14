# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2025 NITK Surathkal

"""To execute gnuplot commands within the engine"""
import os
import subprocess


def build_gnuplot(directory, path_plt, plt_script):
    """
    Executes the gnuplot command with the given script.

    This function creates a gnuplot script file in the specified directory, writes
    the plotting commands to it, and then executes the script using gnuplot.

    Parameters
    ----------
    directory : str
        The directory where the gnuplot script will be created.
    path_plt : str
        The name of the gnuplot script file (e.g., "plot_script.plt").
    plt_script : str
        The gnuplot commands to be written into the script file.

    Returns
    -------
    bool
        True if gnuplot execution succeeds, False otherwise.

    """

    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Directory not found: {directory}")

    plot_path = os.path.join(directory, path_plt)

    try:
        with open(plot_path, "w") as pltfile:
            pltfile.write(plt_script)

        # To execute gnuplot command via gnuplot script
        subprocess.run(["gnuplot", plot_path], check=True)
        return True

    except PermissionError as permission_error:
        raise PermissionError(
            f"Permission denied: Unable to write to {plot_path}"
        ) from permission_error
    except subprocess.CalledProcessError as gnuplot_error:
        raise RuntimeError("Gnuplot execution failed") from gnuplot_error
