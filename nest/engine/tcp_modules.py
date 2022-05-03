# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""TCP module commands"""
import logging
from .exec import exec_subprocess

logger = logging.getLogger(__name__)

# pylint: disable=line-too-long
def is_module_loaded(cong_algo):
    """
    util to check if a module is loaded

    Parameters
    ----------
    cong_algo : str
        TCP congestion algorithm

    Returns
    -------
    bool
        true if the `TCP module` is loaded
    """
    if (
        cong_algo
        in exec_subprocess(
            "sysctl -n net.ipv4.tcp_available_congestion_control",
            output=True,
        ).split()
    ):
        return True
    return False


def set_tcp_params(cong_algo, tcp_module_params, reset_flag=False):
    """
    Change TCP module parameters

    Parameters
    ----------
    cong_algo : str
        TCP congestion algorithm
    tcp_module_params : dict
        TCP module parameters
    reset_flag : boolean
        Set or reset the tcp parameters
    """
    for key, value in tcp_module_params.items():
        if (
            exec_subprocess(
                f"ls -l /sys/module/tcp_{cong_algo}/parameters/{key}",
                output=True,
            )[2]
            == "w"
        ):
            exec_subprocess(
                f"echo -n {value} > /sys/module/tcp_{cong_algo}/parameters/{key}",
                shell=True,
            )
        elif not reset_flag:
            default_value = exec_subprocess(
                f"cat /sys/module/tcp_{cong_algo}/parameters/{key}",
                output=True,
            )
            logger.warning(
                "%s:%s parameter not modifiable. Parameter set to default value - %s",
                cong_algo,
                key,
                default_value,
            )


def load_tcp_module(cong_algo, params_string):
    """
    Load TCP module with parameters

    Parameters
    ----------
    cong_algo : str
        TCP congestion algorithm
    params_string : str
        TCP module parameters
    """
    exec_subprocess(f"modprobe tcp_{cong_algo} {params_string}")


def get_current_params(cong_algo):
    """
    util to get the current parameters of a loaded TCP module

    Parameters
    ----------
    cong_algo : str
        TCP congestion algorithm

    Returns
    -------
    dict
        current parameters
    """
    params = {}
    param_names = exec_subprocess(
        f"ls /sys/module/tcp_{cong_algo}/parameters/",
        output=True,
    ).split()
    for param_name in param_names:
        param_value = exec_subprocess(
            f"cat /sys/module/tcp_{cong_algo}/parameters/{param_name}",
            shell=True,
            output=True,
        ).strip()
        params[param_name] = param_value
    return params


def remove_tcp_module(cong_algo):
    """
    Remove congestion algorithm TCP module

    Parameters
    ----------
    cong_algo : str
        TCP congestion algorithm
    """
    exec_subprocess(f"modprobe -r tcp_{cong_algo}")
