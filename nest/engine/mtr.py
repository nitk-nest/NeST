# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2023 NITK Surathkal

"""mtr command"""

from .exec import exec_subprocess_with_live_output


def mtr(ns_name, dest_addr, protocol, max_ttl, count):
    """
    Runs the mtr command from ns_name to dest_addr.
    Parameters
    ----------
    ns_name : str
        namespace name
    dest_addr : str
        address to mtr to
    protocol : str
        The protocol to use for the Mytraceroute.
    max_ttl : int
        The maximum time to live (TTL) to use for the Mytraceroute.
    count : int
        The number of packets sent to destination.
    live_output : bool
        Show live output of ping packets

    Returns
    -------
    bool
        success of mtr
    """

    status = exec_subprocess_with_live_output(
        f"ip netns exec {ns_name} mtr -t -r -c {count} {protocol}\
        -m {max_ttl} -b {dest_addr}"
    )

    return status == 0
