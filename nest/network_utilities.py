# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Necessary checks before running utilities on experiment"""

import functools
from time import sleep
import nest.config as config
import nest.global_variables as g_var
from nest.topology_map import TopologyMap
from nest.engine.ipv6_states import check_ipv6_states


def ipv6_dad_check(func):
    """
    If DAD is enabled, verifies the state of interfaces
    """

    @functools.wraps(func)
    def wrapper_dad_check(*args, **kwargs):
        """
        Wrapper function for DAD

        Parameters
        ----------
        *args : Non-Keyword Arguments
            passes variable number of arguments to a function
        **kwargs : Keyword Arguments
            passes keyworded, variable-length argument list to a function

        Returns
        -------
        func
            Function to be executed after wrapper is executed
        """

        if (
            g_var.IS_IPV6 is True
            and config.get_value("disable_dad") is not True
            and g_var.IS_DAD_CHECKED is not True
        ):

            namespaces = TopologyMap.get_namespaces()

            # Verifies if IPv6 states are addressable or not
            while True:
                status = check_ipv6_states(namespaces)

                # IPv6 state will be both in tentative and dadfailed together
                if status["dadfailed"][0] is True:
                    raise Exception(
                        "Duplicate address found "
                        f"at interface of node {status['dadfailed'][1]}."
                        "\nExiting ...."
                    )

                # Wait if IPv6 interface is in tentative state
                if status["tentative"] is True:
                    sleep(1)
                else:
                    break
            g_var.IS_DAD_CHECKED = True
        return func(*args, **kwargs)

    return wrapper_dad_check
