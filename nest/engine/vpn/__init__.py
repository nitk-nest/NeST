# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2023 NITK Surathkal

"""
The vpn sub-package provides low-level APIs
for emulating a virtual private network.

Sub-modules:
------------
pki : PKI management functions for generating certificates,
      keys, and certificate authorities
client : Functions for running an OVPN client
server : Functions for running an OVPN server
"""

from .pki import (
    init_pki,
    build_ca,
    build_dh,
    build_client_keypair,
    build_server_keypair,
)
from .server import run_ovpn_server
from .client import run_ovpn_client
