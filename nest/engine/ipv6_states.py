# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""IPv6 States Check"""

from .exec import exec_subprocess


def check_ipv6_states(namespaces):
    """
    Checks IPv6 states

    Parameters
    ----------
    ns_name : str
        namespace name

    Returns
    -------
    dict
        Returns dictionary of states for IPv6 addresses
    """

    states = {
        "tentative": False,
        "dadfailed": [
            False,
        ],
    }

    # Checks in all the namespaces if any interface is in tentative state or not
    for i in range(len(namespaces)):
        status = exec_subprocess(
            f"ip netns exec {namespaces[i]['id']} ip addr show | grep -c tentative",
            shell=True,
            output=True,
        )

        if int(status) != 0:
            states["tentative"] = True
            break

    # Checks in all the namespaces if any interface is in dadfailed state or not
    for i in range(len(namespaces)):
        status = exec_subprocess(
            f"ip netns exec {namespaces[i]['id']} ip addr show | grep -c dadfailed",
            shell=True,
            output=True,
        )

        if int(status) != 0:
            states["dadfailed"][0] = True
            states["dadfailed"].append(namespaces[i]["name"])
            break

    return states
