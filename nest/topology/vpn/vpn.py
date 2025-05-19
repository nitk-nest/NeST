# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2023 NITK Surathkal

"""
API implementation of `connect_vpn`.
"""


import logging
from ipaddress import ip_network
from nest.engine.vpn import (
    init_pki,
    build_ca,
    build_dh,
    build_client_keypair,
    build_server_keypair,
    run_ovpn_client,
    run_ovpn_server,
)
from nest.topology.network import Network
from nest.topology import Node
from nest.topology.interface import BaseInterface
from nest.topology.device import Device
from nest.engine.util import is_dependency_installed

log = logging.getLogger(__name__)


# pylint: disable=too-many-arguments
def start_server(
    server_node: Node,
    server_name: str,
    network_address: str,
    subnet_mask: str,
    protocol: str,
    port: int,
):
    """
    Re-initializes the PKI, creates a CA, generates Diffie-Hellman parameters,
    generates a public-private keypair, and starts an OpenVPN server on the
    given node.

    Parameters
    ----------
    server_node : Node
         The node on which to start the OpenVPN server.
    server_name : str
         The name to assign to the server.
    network_address : str
         The IP address of the VPN network.
    subnet_mask : str
         The subnet mask of the VPN network.
    protocol : str
        The protocol to be used (e.g., "udp" or "tcp").
    port : int
        The port number for the OpenVPN server

    Returns
    --------
    BaseInterface
        A BaseInterface object pointing to the tun device created by the VPN.
    """
    # Re-initialize the PKI
    if init_pki():
        log.info("PKI re-initialized")

    # Create a Certificate Authority
    if build_ca():
        log.info("Certificate Authority Created")

    # Generate Diffie-Hellman parameters
    log.info("Generating Diffie-Hellman parameters. This step will take time.")
    if build_dh():
        log.info("Diffie-Hellman parameters generated")

    # Generate a public-private keypair for the server
    if build_server_keypair(server_name):
        log.info("Keypair generated for server")

    # Start the OpenVPN server and get the tun IP address
    tun_ip = run_ovpn_server(
        server_node.id, server_name, network_address, subnet_mask, protocol, port
    )

    assert tun_ip != "", "Failed to start OpenVPN server"

    # Create a BaseInterface object pointing to the tun device created
    # by the VPN
    tun_interface = BaseInterface("tun", Device(server_node.name, server_node.id))
    tun_interface.set_address(tun_ip)

    return tun_interface


def start_client(
    client_node: Node, client_name: str, server_ip: str, protocol: str, port: int
):
    """
    Generates a public-private keypair for a given client node and starts an
    OpenVPN client on that node.

    Parameters
    ----------
    client_node : Node
        The node on which to start the OpenVPN client
    client_name : str
        The name to assign to the OpenVPN client
    server_ip : str
        The IP address of the OpenVPN server to which the client will connect.
    protocol : str
        The protocol to be used (e.g., "udp" or "tcp").
    port : int
        The port number for the OpenVPN client.

    Returns
    --------
    BaseInterface
        A BaseInterface object pointing to the tun device created by the VPN.
    """

    # Generate keypair for client
    if build_client_keypair(client_name) is True:
        log.info("Keypair generated for client")

    # Start OpenVPN client and get tun interface IP
    tun_ip = run_ovpn_client(client_node.id, client_name, server_ip, protocol, port)

    assert tun_ip != "", "Failed to start OpenVPN client"

    # Create BaseInterface object pointing to tun device
    tun_interface = BaseInterface("tun", Device(client_node.name, client_node.id))
    tun_interface.set_address(tun_ip)

    return tun_interface


# pylint: disable=too-many-locals
def connect_vpn(
    server: Node,
    *clients: Node,
    network: Network,
    protocol: str = "udp",
    port: int = 1194,
):
    """
    Connects a VPN server to multiple VPN clients

    Parameters
    ----------
    server : Node
        The node representing the VPN server.
    *clients : Node
        One or more nodes representing the VPN clients.
    network : Network
        The VPN network to which the nodes will be connected
    protocol : str, optional
        The protocol to be used for the VPN connection (default is "udp")
    port : int, optional
        The port number to be used for the VPN connection (default is 1194)
    Returns
    -------
    Tuple[BaseInterface]
        A tuple containing one Interface object for each client and the server
    """
    # Check if protocol is valid
    if protocol not in ["tcp", "udp"]:
        raise ValueError("Invalid protocol. Use 'tcp' or 'udp'.")

    # Check if port is in the valid range
    if not 0 <= port <= 65535:
        raise ValueError("Invalid port number")

    # Check if the required tools are installed
    required_tools = ["openvpn", "/usr/share/easy-rsa/easyrsa"]
    for tool in required_tools:
        if not is_dependency_installed(tool):
            raise ValueError(
                f"{tool} is not installed.\n Install using 'sudo apt install openvpn easy-rsa'"
            )

    # List to hold the Interface objects for each client and the server
    tun_interfaces = []

    # Set the name, IP address, and subnet mask for the VPN server
    server_name = "server"
    network_ip = ip_network(network.net_address.get_addr())
    network_address = str(network_ip.network_address)
    subnet_mask = str(network_ip.netmask)

    # Start the OpenVPN server and add its tun interface to the list
    interface = start_server(
        server, server_name, network_address, subnet_mask, protocol, port
    )
    tun_interfaces.append(interface)

    # Get the IP address of the server to pass to the clients
    server_ip = server.interfaces[0].get_address().get_addr(with_subnet=False)

    # Start the OpenVPN client for each specified client and add its tun
    # interface to the list
    client_no = 0
    for client in clients:
        client_name = "client" + str(client_no)
        client_no += 1
        interface = start_client(client, client_name, server_ip, protocol, port)
        tun_interfaces.append(interface)

    # Return the list of BaseInterface objects as a tuple
    return tuple(tun_interfaces)
