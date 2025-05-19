# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2023 NITK Surathkal

"""Client side of a many-clients <-> one-server OpenVPN configuration"""

from nest.engine.exec import exec_subprocess_in_background
from nest.topology.address import Address
from nest.engine.vpn.server import get_tun_ip_address


def run_ovpn_client(
    ns_name: str,
    client_name: str,
    server_ip: str,
    proto: str,
    port: int,
) -> Address:
    """
    Starts an OpenVPN client in the specified namespace and connects it
    to the specified server.

    Parameters
    ----------
    ns_name : str
        The name of the namespace in which to start the client.
    client_name : str
        The name to assign to the OpenVPN client.
    server_ip : str
        The IP address of the OpenVPN server to which the client will connect.
    proto : str
        The protocol to be used (e.g., "udp" or "tcp").
    port : int
        The port number for the OpenVPN client.

    Returns
    -------
    Address
        The IP address assigned to the VPN client's tun interface.
    """
    # Construct the OpenVPN command to run in the namespace.
    cmd = f"""ip netns exec {ns_name} openvpn
        --client
        --proto {proto}
        --remote {server_ip}
        --port {port}
        --dev tun{port}
        --nobind
        --ca pki/ca.crt
        --cert pki/issued/{client_name}.crt
        --key pki/private/{client_name}.key
        --float"""

    # Start the OpenVPN client in the namespace.
    exec_subprocess_in_background(
        cmd, wait_for_exit_code=True, exit_text="Initialization Sequence Completed"
    )

    address = get_tun_ip_address(ns_name, port)

    # Return the IP address as an Address object.
    return Address(address)
