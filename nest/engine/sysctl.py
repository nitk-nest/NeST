# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Sysctl commands"""

from .exec import exec_subprocess

def en_ip_forwarding(ns_name):
    """
    Enables ip forwarding in a namespace. Used for routers

    Parameters
    ----------
    ns_name : str
        namespace name
    """
    exec_subprocess(f'ip netns exec {ns_name} sysctl -w net.ipv4.ip_forward=1')

def configure_kernel_param(ns_name, prefix, param, value):
    """
    Configure kernel parameters using sysctl

    Parameters
    ----------
    ns_name : str
        name of the namespace
    prefix : str
        path for the sysctl command
    param : str
        kernel parameter to be configured
    value : str
        value of the parameter
    """
    exec_subprocess(f'ip netns exec {ns_name} sysctl -q -w {prefix}{param}={value}')


def read_kernel_param(ns_name, prefix, param):
    """
    Read kernel parameters using sysctl

    Parameters
    ----------
    ns_name : str
        name of the namespace
    prefix : str
        path for the sysctl command
    param : str
        kernel parameter to be read

    Returns
    -------
    str
        value of the `param`
    """
    value = exec_subprocess(f'ip netns exec {ns_name} sysctl -n {prefix}{param}', output=True)
    return value.rstrip('\n')
