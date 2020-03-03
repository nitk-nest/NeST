# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import time
import json
import os, pwd, grp
import copy
# import atexit

class Configuration():
    """
    Static class responsible for creating JSON 
    configuration file for a given topology
    """

    # static dict to hold all the Configuration objects
    config = {}

    # User and group ID of user running `nest`
    _user_id = ''
    _group_id = ''

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
    def _set_user_id(user_id):
        """
        Set current user id

        :param user_id: user id of current user
        :type current_user: int
        """

        Configuration._user_id = user_id

    @staticmethod
    def _set_group_id(group_id):
        """
        Set current group id

        :param current_user: group id of current user
        :type current_user: int
        """

        Configuration._group_id = group_id

    @staticmethod
    def _add_stats_to_plot(namespace, stat):
        """
        Add stats required to be plotted

        :param namespace: router or client namespace
        :type namespace: Node or Router
        :param stat: statistic to be plotted
        :type stat: string
        """

        prev_stats = copy.deepcopy(Configuration.config[namespace.id]['stats_to_plot'])
        prev_stats.append(stat)
        # stats can be plotted only for client or router
        if Configuration._get_host_type(namespace) != 'SERVER':
            Configuration.config[namespace.id]['stats_to_plot'] = prev_stats

    @staticmethod
    def generate_config_file(filename=None):
        """
        Generate JSON config file for the given topology

        :param filename: File name of config file
        :type filename: string
        """

        # generate a file name based on timestamp
        Configuration.sort_config()
        if filename is None:
            filename = 'config-' + time.strftime('%d-%m-%Y-%H:%M:%S') + '.json'
        # check if filename has json extension
        elif filename[-5:] != '.json':
            filename += '.json'

        
        json_config = json.dumps(Configuration.config, indent=4)

        with open(filename, 'w') as f:
            f.write(json_config)
        
        # Change file permissions to that of user
        user_id = Configuration._user_id
        group_id = Configuration._group_id
        os.chown(filename, user_id, group_id)

    def sort_config():
        """
        Sorts the configuration dict such that all the server
        devices are in the start of the file. This is required 
        as all the servers are to be run first 
        """
        config_copy = Configuration.config
        config_list = [(k, v) for k, v in config_copy.items()]
        # print(config_list[0][1])
        start = 0
        end = len(config_list) - 1
        count = 0

        while start < end:
            if config_list[start][1]['host_type'] == 'SERVER' and config_list[end][1]['host_type'] != 'SERVER':
                start = start + 1
                end = end -1
                continue

            if config_list[start][1]['host_type'] == 'SERVER':
                start = start + 1
            elif config_list[end][1]['host_type'] != 'SERVER':
                end = end - 1
            else:
                temp = config_list[start]
                config_list[start] = config_list[end]
                config_list[end] = temp
                start = start + 1
                end = end - 1

        Configuration.config = dict(config_list)


# Generate json dump on exit

# NOTE: This is not a good solution since a config file is generated
# everytime nest command is run. Even if a topology file is not given
# as input

# atexit.register(lambda : Configuration.generate_config_file())