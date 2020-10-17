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

def create_quagga_directory(dir_path):
    """
    Create a quagga owned directory for quagga configs

    Parameters
    ----------
    dir_path : str
        path to config directory
    """
    cmd = f'sudo -u quagga -g quaggavty mkdir {dir_path}'
    exec_subprocess(cmd)

def create_conf_file(filename):
    """
    Create a quagga owned config file

    Parameters
    ----------
    filename : str
        path to config file
    """
    cmd = f'sudo -u quagga -g quaggavty touch {filename}'
    exec_subprocess(cmd)
