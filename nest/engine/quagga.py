# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""quagga commands"""

from .exec import exec_subprocess


def run_zebra(ns_id, conf_file, pid_file):
    """
    Runs the zebra daemon

    Parameters
    ----------
    ns_id : str
        namespace of the router
    conf_file : str
        path to config file
    pid_file : str
        path to pid file
    """
    cmd = f'ip netns exec {ns_id} zebra --config_file {conf_file} --pid_file {pid_file} --retain'
    exec_subprocess(cmd, block=False)

def run_ripd(ns_id, conf_file, pid_file):
    """
    Runs the zebra daemon

    Parameters
    ----------
    ns_id : str
        namespace of the router
    conf_file : str
        path to config file
    pid_file : str
        path to pid file
    """
    cmd = f'ip netns exec {ns_id} ripd --config_file {conf_file} --pid_file {pid_file} --retain'
    exec_subprocess(cmd, block=False)

def run_ospfd(ns_id, conf_file, pid_file):
    """
    Runs the zebra daemon

    Parameters
    ----------
    ns_id : str
        namespace of the router
    conf_file : str
        path to config file
    pid_file : str
        path to pid file
    """
    cmd = f'ip netns exec {ns_id} ospfd --config_file {conf_file} --pid_file {pid_file}'
    exec_subprocess(cmd, block=False)


def chown_quagga(path):
    """
    Change ownership of quagga config directory and files to quagga

    Parameters
    ----------
    path : str
        path to file or directory
    """
    cmd = f'sudo chown quagga {path}'
    exec_subprocess(cmd)
