# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import time
import json
# import atexit

class Configuration():
    """
    Static class responsible for creating JSON 
    configuration file for a given topology
    """

    # static dict to hold all the Configuration objects
    config = {}

    def __init__(self, namespace, host_type = '', test='', destination='', stats_to_plot=[]):
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
    def _get_host_type(namespace):
        """
        Getter for host_type of a namespace

        :param namespace: Get host type of `this` namespace
        :type namespace: Namespace

        :return: host_type of namespace
        :r_type: string
        """

        return Configuration.config[namespace.id]['host_type']

    @staticmethod
    def _set_host_type(namespace, new_host_type):
        """
        Update host_type of a namespace in `config`

        :param new_host_type: New host type to update to
        :type new_host_type: string
        """

        Configuration.config[namespace.id]['host_type'] = new_host_type

    @staticmethod
    def _add_server(namespace):
        """
        Add server application to namespace in Configuration

        :param namespace: Add server application in this `namespace`
        :type namespace: Namespace
        """

        host_type = Configuration._get_host_type(namespace)
        
        if host_type == 'CLIENT':
            host_type = 'SERVER_' + host_type
        else:
            host_type = 'SERVER'

        Configuration._set_host_type(namespace, host_type)

    @staticmethod
    def _add_client(namespace):
        """
        Add client application to namespace in Configuration

        :param namespace: Add client application in this `namespace`
        :type namespace: Namespace
        """

        host_type = Configuration._get_host_type(namespace)
        
        if host_type == 'SERVER':
            host_type = host_type + "_CLIENT" 
        else:
            host_type = 'CLIENT'

        Configuration._set_host_type(namespace, host_type)

    @staticmethod
    def _set_destination(namespace, new_destination):
        """
        Update destination of a namespace in `config`

        :param namespace: Update destination of this `namespace`
        :type namespace: Namespace
        :param new_destination: New destination to update to
        :type new_destination: string
        """

        Configuration.config[namespace.id]['destination'] = new_destination

    @staticmethod
    def generate_config_file(filename=None):
        """
        Generate JSON config file for the given topology

        :param filename: File name of config file
        :type filename: string
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

# NOTE: This is not a good solution since a config file is generated
# everytime nest command is run. Even if a topology file is not given
# as input

# atexit.register(lambda : Configuration.generate_config_file())