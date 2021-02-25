# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Sysctl commands"""
import logging
from .exec import exec_subprocess

logger = logging.getLogger(__name__)


def en_ip_forwarding(ns_name, ipv4=True, ipv6=True):
    """
    Enables ip forwarding in a namespace. Used for routers

    Parameters
    ----------
    ns_name : str
        namespace name
    ipv4 : bool
        if `True`, enables ipv4 ip forwarding
    ipv6 : bool
        if `True`, enables ipv6 ip forwarding
    """
    if ipv6:
        exec_subprocess(
            f"ip netns exec {ns_name} sysctl -w net.ipv6.conf.all.forwarding=1"
        )
    if ipv4:
        exec_subprocess(f"ip netns exec {ns_name} sysctl -w net.ipv4.ip_forward=1")


def disable_dad(ns_name, int_name):
    """
    Disables DAD at nodes for IPv6 Addressing

    Parameters
    ----------
    ns_name : str
        namespace name
    int_name : str
        interface name
    """
    exec_subprocess(
        f"ip netns exec {ns_name} sysctl -w net.ipv6.conf.{int_name}.accept_dad=0"
    )


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
    exec_subprocess(f"ip netns exec {ns_name} sysctl -q -w {prefix}{param}={value}")


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
    value = exec_subprocess(
        f"ip netns exec {ns_name} sysctl -n {prefix}{param}", output=True
    )
    return value.rstrip("\n")


def set_mpls_max_label_node(ns_name, max_num_labels):
    """
    Sets the maximum mpls label for the namespace

    Parameters
    ----------
    ns_name: str
    max_num_labels: int
    """
    exec_subprocess(
        f"ip netns exec {ns_name} sysctl -w net.mpls.platform_labels={max_num_labels}"
    )
    try:
        max_label = int(
            exec_subprocess(
                f"ip netns exec {ns_name} sysctl -n net/mpls/platform_labels",
                output=True,
            )
        )
        if max_label != max_num_labels:
            logger.error(
                "platform_labels for node %s wasn't set to %s!",
                str(ns_name),
                str(max_num_labels),
            )
            logger.error("Ensure mpls kernel modules are loaded")
    except ValueError:
        logger.error(
            "Couldn't set platform_labels. Ensure mpls kernel modules are loaded"
        )


def enable_mpls_interface(ns_name, dev_name):
    """
    Enable mpls input to interface through sysctl.

    Parameters
    ----------
    ns_name: str
    dev_name: str
    """
    exec_subprocess(
        f"ip netns exec {ns_name} sysctl -w net.mpls.conf.{dev_name}.input=1",
        output=True,
    )
    try:
        input_val = int(
            exec_subprocess(
                f"ip netns exec {ns_name} sysctl -n net.mpls.conf.{dev_name}.input",
                output=True,
            )
        )
        if input_val == 0:
            logger.error("Couldn't enable mpls input for interface %s!!", dev_name)
    except ValueError:
        logger.error(
            "Couldn't enable mpls input. Ensure mpls kernel modules are loaded"
        )
