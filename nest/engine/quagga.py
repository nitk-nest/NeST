# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""quagga commands"""

from .exec import exec_subprocess

def run_quagga(ns_id, daemon, conf_file, pid_file):
    """
    Runs quagga related daemons like zebra, ospf and rip

    Parameters
    ----------
    ns_id : str
        namespace of the router
    daemon : str
        quagga process to run(one of ['zebra'. 'ospfd])
    conf_file : str
        path to config file
    pid_file : str
        path to pid file
    """
    cmd = f'ip netns exec {ns_id} {daemon} -f {conf_file} -i {pid_file} -d'
    exec_subprocess(cmd)

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
