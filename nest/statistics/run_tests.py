# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# Script to be run for running tests on the namespaces
# with the json file configurations as command line arguments

import subprocess
import argparse
import json
from .ss_parse import parse_ss


def run_test_commands(cmd):
    proc = subprocess.Popen(
        cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def run_netserver(ns_name):
    cmd = 'ip netns exec {} netserver'.format(ns_name)
    run_test_commands(cmd)


def run_netperf(ns_name, destination_ip):
    cmd = 'ip netns exec {} netperf -H {}'.format(ns_name, destination_ip)
    run_test_commands(cmd)


def fetch_host_stats(ns_name, config):
    parse_ss(ns_name, config['destination'], config['stats_to_plot'] , 2)


def fetch_router_stats(ns_name):
    pass


def parse_config(config_files):
    """

    Parses the config files to run tests accordingly
    """

    # Loop through all the config files, convert each config file to
    # a dict and run netserver or/and netperf depending on the type of
    # host.
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
