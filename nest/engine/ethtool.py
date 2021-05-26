# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal
"""enabling/disabling offloads"""
import logging
from .exec import exec_subprocess

logger = logging.getLogger(__name__)


def enable_offloads(namespace_id, interface_id, offload_type):
    """
    enable offload
    Parameters
    ----------
    namespace_id : str
        The namespace id on which interface is available
    interface_id : str
            The interface id where offloads enable
    offload_type : str
            The type of offloads that need to be enabled

    Returns
    --------
    bool
        success of ethtool command
    """
    status = exec_subprocess(
        f"ip netns exec {namespace_id} ethtool -K {interface_id} {offload_type} on "
    )
    return status == 0


# Disable Offloads
def disable_offloads(namespace_id, interface_id, offload_type):
    """
    disable offload
    Parameters
    ----------
    namespace_id : str
        The namespace id on which interface is available
    interface_id : str
        The interface id where offloads disable
    offload_type : str
        The type of offloads that need to be disabled

    Returns
    -------
    bool
        success of ethtool command
    """
    status = exec_subprocess(
        f"ip netns exec {namespace_id} ethtool -K {interface_id} {offload_type} off "
    )
    return status == 0
