# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import time
import json
import atexit

class Configuration():
    """
    Static class responsible for creating JSON 
    configuration file for a given topology
    """

    # static dict to hold all the Configuration objects
    config = {}

    def __init__(self, namespace, host_type, test='', destination='', stats_to_plot=[]):
        """
        Constructor which adds namespace to `Configuration.config` 
        static object

        :param namespace: Namespace object
        :type namespace: Namespace
        :param host_type: 'Node' or 'Router'
        :type host_type: string
        :param test: Test to be run on the namespace
        :type test: string

        **TODO**: Add comments to other parameters
        """
        self.namespace_name = namespace.name
        self.host_type = host_type
        self.test = test
        self.destination = destination
        self.stats_to_plot = stats_to_plot

        Configuration.config[namespace.id] = self.__dict__
    
    @staticmethod
    def generate_config_file(filename=None):
        """
        Generate JSON config file for the given topology
        """

        # generate a file name based on timestamp
        if filename is None:
            filename = 'config-' + time.strftime('%d-%m-%Y-%H:%M:%S') + '.json'
        # check if filename has json extension
        elif filename[-5:] != '.json':
            filename += '.json'

        
        json_config = json.dumps(Configuration.config, indent=4)

        with open(filename, 'w') as f:
            f.write(json_config)

# Generate json dump on exit
atexit.register(lambda : Configuration.generate_config_file())