# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019 NITK Surathkal

# Define network topology creation helpers
from address import Address

class Namespace:

    def __init__(self):
        # Assign unique iproute2 name
        self.id = id(self)
        self.interfaces = []

    def add_route(self, dest_addr, nxt_hop_addr, via_int):
        pass

class Node(Namespace):

    def __init__(self):
        pass
        # Create namespace in iproute2

class Router(Namespace):

    def __init__(self):

        Namespace.__init__(self)

        # Enable forwarding
        enable_forwarding(Node.id)
