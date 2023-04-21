# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2023 NITK Surathkal

"""MPTCP commands"""

import logging
import re
import sys
from .exec import exec_subprocess, exec_subprocess_in_background

logger = logging.getLogger(__name__)


def check_compatibility(func):
    """
    Decorator to check if the system supports MPTCP
    """

    def wrapper(*args, **kwargs):
        if not compatible_iproute2_version():
            logger.error("This system does not support MPTCP.")
            sys.exit()
        return func(*args, **kwargs)

    return wrapper


def mptcp_preload_string(is_mptcp):
    """
    MPTCP Preload String

    Parameters
    ----------
    is_mptcp: bool
        boolean to determine if connection is MPTCP enabled

    Returns
    -------
    str:
        The mptcpize run preload string
    """
    return "mptcpize run " if is_mptcp else ""


@check_compatibility
def set_mptcp_node_parameters(max_subflows, max_add_addr_accepted, ns_name):
    """
    Set MPTCP node parameters

    Parameters
    ----------
    max_subflows: int
    max_add_addr_accepted: int
    ns_name: str
    """
    exec_subprocess(
        f"ip -n {ns_name} mptcp limits set "
        f"subflow {max_subflows} add_addr_accepted {max_add_addr_accepted} ",
        output=True,
    )


@check_compatibility
def add_mptcp_monitor(ns_name, folder):
    """
    Add and log MPTCP monitor
    """
    exec_subprocess_in_background(
        f"ip netns exec {ns_name} ip mptcp monitor "
        f"> {re.escape(folder)}/mptcp_monitor_{ns_name}.log &",
        shell=True,
    )


@check_compatibility
def enable_mptcp_node(ns_name):
    """
    Enable MPTCP Node

    Parameters
    ----------
    ns_name: str
    """
    exec_subprocess(
        f"ip netns exec {ns_name} sysctl -w net.mptcp.enabled=1",
        output=True,
    )
    exec_subprocess(
        f"ip -n {ns_name} mptcp endpoint flush",
        output=True,
    )


@check_compatibility
def disable_mptcp_node(ns_name):
    """
    Disable MPTCP Node

    Parameters
    ----------
    ns_name: str
    """
    exec_subprocess(
        f"ip netns exec {ns_name} sysctl -w net.mptcp.enabled=0",
        output=True,
    )
    exec_subprocess(
        f"ip -n {ns_name} mptcp endpoint flush",
        output=True,
    )


@check_compatibility
def enable_mptcp_endpoint(ns_name, interface, flags):
    """
    Set interface as an MPTCP endpoint

    Parameters
    ----------
    ns_name: str
    dev_name: Interface
    flags[]: An array of Strings
    """
    if len(set(flags) - set(possible_mptcp_flags)) == 0:
        exec_subprocess(
            f"ip -n {ns_name} "
            f"mptcp endpoint add {interface.get_address().get_addr(with_subnet=False)} "
            f"dev {interface.id} {' '.join(flags)}",
            output=True,
        )
    else:
        logger.error("Not a valid parameter")


@check_compatibility
def get_mptcp_endpoints(ns_name, interface=None):
    """
    Gets the MPTCP endpoints of the interface

    Parameters
    ----------
    ns_name: str
    interface: Interface
    """
    raw_output = exec_subprocess(
        f"ip -n {ns_name} mptcp endpoint show",
        output=True,
    )

    endpoint_matches = dict(
        list(
            map(
                lambda endpoint: [
                    re.match(r"(.*) id", endpoint).group(1),
                    re.findall(r"(subflow|signal|backup|fullmesh)", endpoint),
                ],
                re.findall(
                    r".*dev " + (interface.id if interface else r"\w+"), raw_output
                ),
            )
        )
    )

    return endpoint_matches


def __get_iproute2_version():
    """
    Get iproute2 version

    Returns
    -------
    str:
        The extracted version from the terminal output
    """
    output_string = exec_subprocess("ip -V", output=True)
    version_match = re.search(r"iproute2-(\d*.\d*.\d*)", output_string)
    if version_match:
        return version_match.group(1)
    return None


def compatible_iproute2_version():
    """
    Compare the installed iproute2 version with the threshold.
    Versions above 5.15.0 support the ip-mptcp API.

    Returns
    -------
    bool:
        False if the installed version is older than 5.15.0
    """
    threshold_version = (5, 15, 0)
    version_on_system = __get_iproute2_version()

    try:
        parsed_version_tuple = tuple(map(int, version_on_system.split(".")))
        if parsed_version_tuple < threshold_version:
            return False

    except ValueError:
        return False

    return True


def __old_iproute2_version():
    """
    Compare the installed iproute2 version with the threshold.
    Versions above 5.19.0 support fullmesh as an endpoint flag for MPTCP.

    Returns
    -------
    bool:
        True if the installed version is older than 5.19.0
    """
    threshold_version = (5, 19, 0)
    version_on_system = __get_iproute2_version()
    if version_on_system is None:
        return True
    return tuple(map(int, version_on_system.split("."))) < threshold_version


@check_compatibility
def get_default_mptcp_flags():
    """
    Set default mptcp flags depending on the version.
    Default value set to "subflow", "signal" if version < 5.19.0
    else default set to "fullmesh", "signal"

    Returns
    -------
    Array:
         consisting of default mptcp flags
    """
    return (
        ["signal", "subflow"]
        if __old_iproute2_version()
        else ["subflow", "fullmesh", "signal"]
    )


def __get_all_possible_flags():
    """
    Get all mptcp flags depending on the version.
    Returns
    -------
    Array:
         returns an array of version compatible flags
    """
    if not compatible_iproute2_version():
        return []
    if __old_iproute2_version():
        return ["subflow", "signal", "backup"]
    return ["subflow", "signal", "backup", "fullmesh"]


possible_mptcp_flags = __get_all_possible_flags()
