# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2023 NITK Surathkal

"""Commands set up OpenVPN PKI using Easy-RSA"""

from nest.engine.exec import exec_subprocess


def init_pki():
    """
    Removes and re-initializes the PKI dir for a clean PKI.

    Returns
    --------
    bool
        The success of the init-pki command.
    """
    # Execute the init-pki command and return
    # whether it was successful.
    status = exec_subprocess("/usr/share/easy-rsa/easyrsa --batch init-pki")
    return status == 0


def build_ca():
    """
    Creates a new CA (Certificate Authority).

    Returns
    --------
    bool
        The success of the build-ca command.
    """
    # Execute the build-ca command in and return
    #  whether it was successful.
    status = exec_subprocess(
        """/usr/share/easy-rsa/easyrsa --batch build-ca
        nopass"""
    )
    return status == 0


def build_dh():
    """
    Generates DH (Diffie-Hellman) parameters.

    Returns
    --------
    bool
        The success of the gen-dh command.
    """
    # Execute the gen-dh command and return
    # whether it was successful.
    status = exec_subprocess("/usr/share/easy-rsa/easyrsa --batch gen-dh")
    return status == 0


def build_client_keypair(client_name: str):
    """
    Generates a keypair and signs locally for a client.

    Parameters
    ----------
    client_name : str
        The name of the client.

    Returns
    --------
    bool
        The success of the build-client-full command.
    """
    # Execute the build-client-full command for the given
    # client name and return whether it was successful.
    status = exec_subprocess(
        f"""/usr/share/easy-rsa/easyrsa --batch build-client-full
        {client_name} nopass"""
    )
    return status == 0


def build_server_keypair(server_name: str):
    """
    Generates a keypair and signs locally for a server.

    Parameters
    ----------
    server_name : str
        The name of the server.

    Returns
    --------
    bool
        The success of the build-server-full command.
    """
    # Execute the build-server-full command for the given
    # server name and return whether it was successful.
    status = exec_subprocess(
        f"""/usr/share/easy-rsa/easyrsa --batch build-server-full
        {server_name} nopass"""
    )
    return status == 0
