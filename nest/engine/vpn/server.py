# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2023 NITK Surathkal

"""Server side of a many-clients <-> one-server OpenVPN configuration"""

from time import sleep
import re
from nest.engine.exec import (
    exec_subprocess_in_background,
    exec_subprocess,
)
from nest.topology.address import Address


def is_port_free(ns_name: str, port: int) -> bool:
    """
    Checks if a port is free within a specified network namespace.

    Parameters
    ----------
    ns_name : str
        The name of the network namespace to check within.
    port : int
        The port number to check.

    Returns
    -------
    bool
        True if the port is free, False if the port is in use.
    """
    cmd = f"ip netns exec {ns_name} netstat -tuln | grep ':{port} '"
    exit_status = exec_subprocess(cmd, shell=True)
    return exit_status == 0  # Port is in use if the command finds a match


def get_tun_ip_address(ns_name, port):
    """
    Retrieve the IP address assigned to the tun interface in
    the specified network namespace.

    Args:
        ns_name (str): Name of the network namespace.

    Returns:
        str: The IP address assigned to the tun interface.

    """
    # Command to retrieve the IP address
    cmd = f"ip netns exec {ns_name} ip addr show tun{port}"

    # Execute the command and capture the output
    output = exec_subprocess(cmd, shell=True, output=True)

    # Define a regular expression to match the IP address
    pattern = r"inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"

    # Search the output for the IP address
    match = re.search(pattern, output)
    # Extract the IP address from the match object
    address = match.group(1)

    return address


# pylint: disable=too-many-arguments
def run_ovpn_server(
    ns_name: str,
    server_name: str,
    network_address: str,
    subnet_mask: str,
    proto: str,
    port: int,
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
    proto : str
        The protocol to be used (e.g., "udp" or "tcp").
    port : int
        The port number for the OpenVPN server.

    Returns
    -------
    Address
        The IP address of the server's tun interface.
    """

    if is_port_free(ns_name, port):
        raise ValueError(
            f"OpenVPN is already running on port {port}. Try using another port."
        )

    # Run OpenVPN server program in the specified namespace,
    # with the given arguments.
    cmd = f"""ip netns exec {ns_name}
        openvpn
        --proto {proto}
        --port {port}
        --dev tun{port}
        --server {network_address} {subnet_mask}
        --ca pki/ca.crt
        --cert pki/issued/{server_name}.crt
        --key pki/private/{server_name}.key
        --dh pki/dh.pem
        --keepalive 10 60"""

    # Start the OpenVPN server in the namespace.
    exec_subprocess_in_background(
        cmd, wait_for_exit_code=True, exit_text="Initialization Sequence Completed"
    )

    # Wait for the server to start by giving it a few seconds to initialize.
    sleep(5)

    address = get_tun_ip_address(ns_name, port)

    return Address(address)
