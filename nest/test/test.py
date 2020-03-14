# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

from ..topology import Address
from ..configuration import Configuration

class Test():

    def __init__(self):
        
        # By default assume localhost for now
        self.src_node = None
        self.src_addr = '127.0.0.1'
        self.dst_addr = '127.0.0.1'
        self.n_flows = 1

    def add_flow(self, source_node, source_address, destination_address, num_of_flows):
        """

        """

        # Verify address passed by user
        if type(source_address) is str:
            source_address = Address(source_address)
        if type(destination_address) is str:
            destination_address = Address(destination_address)

        # TODO: Verify if source_node is actually a node
        self.src_node = source_node
        self.src_addr = source_address.get_addr(without_subnet=True)
        self.dst_addr = destination_address.get_addr(without_subnet=True)
        self.n_flows = num_of_flows

    def run(self):
        """

        """

        print('Running test')
        

