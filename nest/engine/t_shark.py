# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""t_shark API management"""


from .exec import exec_subprocess


def capture_packets(ns_name, **kwargs):
    """
    Executes packet capture using tshark

    Parameters
    ----------
    ns_name : str
        The namespace where packets need to be captured

    """

    tshark_params = ""
    for param, value in kwargs.items():
        tshark_params += param + " " + value + " "

    exec_subprocess(f"ip netns exec {ns_name} tshark {tshark_params} -q")
