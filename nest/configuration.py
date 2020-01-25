# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import time
import json

class Configuration():

    # static dict to hold all the Configuration objects
    config = {}

    def __init__(self, namespace, host_type, test='', destination='', stats_to_plot=[]):
        self.namespace_id = namespace.id
        self.namespace_name = namespace.name
        self.test = test
        self.destination = destination
        self.stats_to_plot = stats_to_plot

        Configuration.config[namespace.id] = self.__dict__
    
    @staticmethod
    def generate_config_file(filename=None):
        # generate a file name based on timestamp
        if filename is None:
            filename = 'config-' + time.strftime('%d-%m-%Y-%H:%M:%S') + '.json'
        # check if filename has json extension
        elif filename[-5:] != '.json':
            filename += '.json'

        
        json_config = json.dumps(Configuration.config, indent=4)

        with open(filename, 'w') as f:
            f.write(json_config)