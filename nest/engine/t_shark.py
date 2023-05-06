# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""t_shark API management"""

import os
import logging
from .exec import exec_subprocess

logger = logging.getLogger(__name__)

# Get the current working directory
current_dir = os.getcwd()


def capture_packets(ns_name, **kwargs):
    """
    Executes packet capture using tshark

    Parameters
    ----------
    ns_name : str
        The namespace where packets need to be captured

    """

    tshark_params = ""
    packet_capture = ""
    for param, value in kwargs.items():
        if param == "-w":
            packet_capture = value

        tshark_params += f"{param} {value} "

    # Set the path for the pcap file in the current directory
    pcap_file = f"{current_dir}/packet_capture/{packet_capture}"

    # Create the directory for the pcap file if it doesn't exist
    os.makedirs(os.path.dirname(pcap_file), exist_ok=True)

    logger.info("The PCAP file is saved in %s", pcap_file)

    exec_subprocess(f"ip netns exec {ns_name} tshark {tshark_params} -w {pcap_file} -q")
    exec_subprocess(f"ip netns exec {ns_name} chmod +r {pcap_file}")
