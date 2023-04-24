# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2023 NITK Surathkal

"""Functions related to ARP table"""

import re
import logging
from .exec import exec_subprocess_with_live_output

logger = logging.getLogger(__name__)


def get_arp_table(ns_name):
    """
    Retrieve and print the ARP table for a specified namespace.

    Parameters
    ----------
    ns_name : str
        The name of the namespace for which to retrieve the ARP table.

    Returns
    -------
    bool
        Returns `True` if the ARP table was successfully retrieved and printed,
        Else `False`
    """
    status = exec_subprocess_with_live_output(f"ip netns exec {ns_name} arp")
    return status == 0


def delete_arp_entry(ns_name, ip_addr):
    """
    Delete a specified ARP table entry for a namespace.

    Parameters
    ----------
    ns_name : str
        The name of the namespace in which to delete the ARP table entry.
    ip_addr : Address
        The IP address of the ARP table entry to be deleted.

    Returns
    -------
    bool
        Returns `True` if the ARP table entry was successfully deleted,
        Else `False`
    """

    status = exec_subprocess_with_live_output(
        f"ip netns exec {ns_name} arp -d {ip_addr}"
    )
    return status


def flush_arp_table(ns_name):
    """
    Flush the entire ARP table for a specified namespace.

    Parameters
    ----------
    ns_name : str
        The name of the namespace for which to flush the ARP table.

    Returns
    -------
    bool
        Returns True if the ARP table was successfully flushed,
        Else `False`
    """
    status = exec_subprocess_with_live_output(
        f"ip netns exec {ns_name} ip -s neigh flush all"
    )
    return status


def get_arp_entry(ns_name, ip_addr):
    """
    Retrieve a specified ARP table entry for a namespace.

    Parameters
    ----------
    ns_name : str
        The name of the namespace from which to retrieve the ARP table entry.
    ip_addr : Address
        The IP address of the ARP table entry to be retrieved.

    Returns
    -------
    bool
        Returns `True` if the ARP table entry was successfully retrieved
        Else `False`
    """
    status = exec_subprocess_with_live_output(f"ip netns exec {ns_name} arp {ip_addr}")
    return status


def set_arp_entry(ns_name, ip_addr, mac_addr):
    """
    Set the ARP table entry for a specified IP address and MAC address from the given node and
    Validate MAC addresses.

    Parameters
    ----------
    ns_name : str
        The name of the namespace from which to retrieve the ARP table entry.
    ip_addr : Address
        The IP address of the ARP table entry to be retrieved.
    mac_address : string
            The MAC address for which to set the ARP table entry.

    Returns
    -------
    bool
        Returns `True` if the ARP table entry was successfully retrieved
        Else `False`
    """
    # regular expression pattern
    mac_address_pattern = "^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$"
    # regular expression pattern matches a MAC address
    if re.match(mac_address_pattern, mac_addr):
        status = exec_subprocess_with_live_output(
            f"ip netns exec {ns_name} arp -s {ip_addr} {mac_addr}"
        )
    else:
        logger.info("%s is not a valid Mac address", mac_addr)
    return status
