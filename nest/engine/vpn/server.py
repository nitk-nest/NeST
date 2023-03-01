# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2023 NITK Surathkal

"""Server side of a many-clients <-> one-server OpenVPN configuration"""

from time import sleep
import re
from nest.engine.exec import exec_subprocess_in_background, exec_subprocess
from nest.topology.address import Address


def get_tun0_ip_address(ns_name):
    """
    Retrieve the IP address assigned to the tun interface in
    the specified network namespace.

    Args:
        ns_name (str): Name of the network namespace.

    Returns:
        str: The IP address assigned to the tun interface.

    """
    # Command to retrieve the IP address
    cmd = f"ip netns exec {ns_name} ip addr show tun0"

    # Execute the command and capture the output
    output = exec_subprocess(cmd, shell=True, output=True)

    # Define a regular expression to match the IP address
    pattern = r"inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"

    # Search the output for the IP address
    match = re.search(pattern, output)

    # Extract the IP address from the match object
    address = match.group(1)

    return address


def run_ovpn_server(
    ns_name: str, server_name: str, network_address: str, subnet_mask: str
):
    """
    Runs the OpenVPN server program in the specified network namespace.

    Parameters
    ----------
    ns_name : str
        The name of the network namespace in which to run the OpenVPN server.
    server_name : str
        The name to assign to the OpenVPN server.
    network_address : str
        The IP address of the OpenVPN server.
    subnet_mask : str
        The subnet mask for the virtual network.

    Returns
    -------
    Address
        The IP address of the server's tun interface.
    """

    # Run OpenVPN server program in the specified namespace,
    # with the given arguments.
    cmd = f"""ip netns exec {ns_name}
        openvpn
        --proto udp
        --port 1194
        --dev tun
        --server {network_address} {subnet_mask}
        --ca pki/ca.crt
        --cert pki/issued/{server_name}.crt
        --key pki/private/{server_name}.key
        --dh pki/dh.pem
        --keepalive 10 60"""

    # Start the OpenVPN server in the namespace.
    exec_subprocess_in_background(cmd, wait_for_exit_code=True)

    # Wait for the server to start by giving it a few seconds to initialize.
    sleep(5)

    address = get_tun0_ip_address(ns_name)

    return Address(address)
