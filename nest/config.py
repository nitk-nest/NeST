# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

""" API's to process config files """

import os
import json

# Importing data from the config files
with open(os.path.realpath(os.path.dirname(__file__)) + '/config.json', 'r') as openfile:
    CONFIG = json.load(openfile)

class Topology():
    """
    Storing data related to Topology module
    """

    def __init__(self):
        self.address_with_subnet = CONFIG['topology']['address_with_subnet']
        self.assign_random_names = CONFIG['topology']['assign_random_names']

    def get_address_with_subnet(self):
        """
        Whether the given addresses have to include subnets or not
        according to config

        Returns
        -------
        bool
            True if subnets are to be given
            else False
        """
        return self.address_with_subnet

    def get_assign_random_names(self):
        """
        Whether program internally assigns randomly generated names to
        the namespaces or uses the user given names

        Returns
        -------
        bool
            True if subnets are to be given
            else False
        """
        return self.assign_random_names

TOPOLOGY = Topology()
