# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Routing commands"""
from os import path
from nest.engine.util import is_dependency_installed
from .. import config
from .exec import exec_subprocess

# Path to routing_suite daemon binaries
FRR_DAEMONPATH = "/usr/lib/frr/"


def run_zebra(ns_id, conf_file, pid_file):
    """
    Runs the zebra daemon

    Parameters
    ----------
    ns_id : str
        namespace of the router
    conf_file : str
        path to config file
    pid_file : str
        path to pid file
    """
    if config.get_value("routing_suite") == "frr":
        cmd = f"ip netns exec {ns_id} {FRR_DAEMONPATH}zebra --config_file {conf_file} \
                --pid_file {pid_file} --vrfwnetns --retain --daemon -N {ns_id}"
    else:
        cmd = f"ip netns exec {ns_id} zebra --config_file {conf_file} \
                --pid_file {pid_file} --retain --daemon"
    exec_subprocess(cmd)


def run_ripd(ns_id, conf_file, pid_file, ipv6, **kwargs):
    """
    Runs the ripd daemon

    Parameters
    ----------
    ns_id : str
        namespace of the router
    conf_file : str
        path to config file
    pid_file : str
        path to pid file
    """

    if config.get_value("routing_suite") == "frr":
        if ipv6:
            cmd = f"ip netns exec {ns_id} {FRR_DAEMONPATH}ripngd --config_file {conf_file} \
                    --pid_file {pid_file} --daemon -N {ns_id}"
        else:
            cmd = f"ip netns exec {ns_id} {FRR_DAEMONPATH}ripd --config_file {conf_file} \
                    --pid_file {pid_file} --daemon -N {ns_id}"
    elif config.get_value("routing_suite") == "bird":
        if config.get_value("routing_logs"):
            cmd = f"ip netns exec {ns_id} bird -c {conf_file} -P {pid_file} \
                     -s {kwargs['socket_file']} -D {kwargs['log_file']}"
        else:
            cmd = f"ip netns exec {ns_id} bird -c {conf_file} -P {pid_file} \
                    -s {kwargs['socket_file']}"
    else:
        if ipv6:
            cmd = f"ip netns exec {ns_id} ripngd --config_file {conf_file} \
                    --pid_file {pid_file} --retain --daemon"
        else:
            cmd = f"ip netns exec {ns_id} ripd --config_file {conf_file} \
                    --pid_file {pid_file} --retain --daemon"
    exec_subprocess(cmd)


def run_ospfd(ns_id, conf_file, pid_file, ipv6, **kwargs):
    """
    Runs the ospfd daemon

    Parameters
    ----------
    ns_id : str
        namespace of the router
    conf_file : str
        path to config file
    pid_file : str
        path to pid file
    """
    if config.get_value("routing_suite") == "frr":
        if ipv6:
            cmd = f"ip netns exec {ns_id} {FRR_DAEMONPATH}ospf6d --config_file {conf_file} \
                --pid_file {pid_file} --daemon -N {ns_id}"
        else:
            cmd = f"ip netns exec {ns_id} {FRR_DAEMONPATH}ospfd --config_file {conf_file} \
                --pid_file {pid_file} --daemon -N {ns_id}"
    elif config.get_value("routing_suite") == "bird":
        if config.get_value("routing_logs"):
            cmd = f"ip netns exec {ns_id} bird -c {conf_file} -P {pid_file} \
                -s {kwargs['socket_file']} -D {kwargs['log_file']}"
        else:
            cmd = f"ip netns exec {ns_id} bird -c {conf_file} -P {pid_file} \
                -s {kwargs['socket_file']}"
    else:
        if ipv6:
            cmd = f"ip netns exec {ns_id} ospf6d --config_file {conf_file} \
            --pid_file {pid_file} --daemon"
        else:
            cmd = f"ip netns exec {ns_id} ospfd --config_file {conf_file} \
                --pid_file {pid_file} --daemon"
    exec_subprocess(cmd)


def run_isisd(ns_id, conf_file, pid_file):
    """
    Runs the isisd daemon

    Parameters
    ----------
    ns_id : str
        namespace of the router
    conf_file : str
        path to config file
    pid_file : str
        path to pid file
    """
    if config.get_value("routing_suite") == "frr":
        cmd = f"ip netns exec {ns_id} {FRR_DAEMONPATH}isisd --config_file {conf_file} \
            --pid_file {pid_file} --daemon -N {ns_id}"
    else:
        cmd = f"ip netns exec {ns_id} isisd --config_file {conf_file} \
            --pid_file {pid_file} --daemon"
    exec_subprocess(cmd)


def run_ldpd(ns_id, conf_file, pid_file):
    """
    Runs the ldp daemon (MPLS)
    Requires frr routing_suite

    Parameters
    ----------
    ns_id : str
        namespace of the router
    conf_file : str
        path to config file
    pid_file : str
        path to pid file
    """
    if config.get_value("routing_suite") == "frr":
        cmd = f"ip netns exec {ns_id} /usr/lib/frr/ldpd --config_file {conf_file} \
            --pid_file {pid_file} --daemon -N {ns_id}"
        exec_subprocess(cmd)
    else:
        raise Exception("Ldp requires Frrouting")


def supports_dynamic_routing(daemon):
    """
    Checks whether frr/quagga/bird is installed

    Parameters
    ----------
    daemon : str
        routing daemon

    Returns
    -------
    bool
        true if frr/quagga/bird is installed
    """

    if (
        config.get_value("routing_suite") == "quagga"
        or config.get_value("routing_suite") == "bird"
    ):
        return is_dependency_installed(daemon)

    if config.get_value("routing_suite") == "frr":
        # /usr/lib/ is the default installation path for frr which is not in PATH.
        # This results in `is_dependency_installed` always returning false for frr, hence we
        # check if the daemon binary exists
        return path.isfile(f"{FRR_DAEMONPATH}{daemon}")

    return False
