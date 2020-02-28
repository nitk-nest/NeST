# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# Script to be run for running tests on the namespaces
# with the json file configurations as command line arguments

import json
from .ss_parse import parse_ss
from .tc_parse import parse_qdisc
from .netperf import run_netperf, run_netserver

def fetch_host_stats(ns_name, config):
    parse_ss(ns_name, config['destination'], config['stats_to_plot'] , 2)


def fetch_router_stats(ns_name, config):
    parse_qdisc(ns_name, config['stats_to_plot'], 2)
    pass


def parse_config(config_files):
    """

    Parses the config files to run tests accordingly
    """

    # Loop through all the config files, convert each config file to
    # a dict and run netserver or/and netperf depending on the type of
    # host.
    # TODO: parallelize this so that all the config files can be run simultaneously
    for config_file in config_files:
        with open(config_file, 'r') as f:
            config = json.load(f)
            for ns_name, values in config.items():
                if values['host_type'] == 'SERVER':
                    run_netserver(ns_name)
                elif values['host_type'] == 'CLIENT':
                    run_netperf(ns_name, values['destination'])
                    fetch_host_stats(ns_name, values)
                elif values['host_type'] == 'SERVER_CLIENT':
                    run_netserver(ns_name)
                    run_netperf(ns_name, values['destination'])
                    fetch_host_stats(ns_name, values)
                elif values['host_type'] == 'ROUTER':
                    fetch_router_stats(ns_name, values)
                elif values['host_type'] == 'INTERFACE':
                    # TODO: fetch interface stats
                    pass
