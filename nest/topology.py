# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019 NITK Surathkal

# Define network topology creation helpers

import Address

# Assume gen_unique_id function

class Node:

    def __init__(self):
        self.id = gen_unique_id()

        # Create namespace in iproute2
        create_ns(self.id)

    # def add_route(self):
    
class Router(Node):

    def __init__(self):

        Node.__init__(self)

        # Enable forwarding
        enable_forwarding(Node.id)
