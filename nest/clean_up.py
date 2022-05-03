# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""
This module contains methods to kill any running processes in namespaces
and delete all namespaces after the experiment is complete.
"""

import atexit
import logging
from nest.network_utilities import ipv6_dad_check
from nest import engine
from . import config

from . import engine
from .topology_map import TopologyMap

logger = logging.getLogger(__name__)


# pylint: disable=import-outside-toplevel
# pylint: disable=cyclic-import
@atexit.register
def tcp_modules_clean_up():
    """Clean up the modified TCP modules"""

    from .experiment.experiment import Experiment

    # Remove newly loaded modules
    for cong_algo in Experiment.new_cong_algos:
        engine.remove_tcp_module(cong_algo)
    (Experiment.new_cong_algos).clear()

    # Reset old modules with original params
    for cong_algo, params in (Experiment.old_cong_algos).items():
        engine.set_tcp_params(cong_algo, params, True)
    (Experiment.old_cong_algos).clear()


def kill_processes():
    """
    Kill any running processes in namespaces
    """
    nodes = TopologyMap.get_nodes()

    for ns_id in nodes:
        engine.kill_all_processes(ns_id)


@atexit.register
@ipv6_dad_check
def delete_namespaces():
    """
    Delete all the newly generated namespaces
    """
    nodes = TopologyMap.get_nodes()

    if config.get_value("delete_namespaces_on_termination"):
        for ns_id in nodes:
            engine.delete_ns(ns_id)
        logger.info("Cleaned up environment!")
    else:
        logger.info("Namespaces not deleted")
