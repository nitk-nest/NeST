# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import argparse, sys
from .. import statistics
from .. import engine

class Argument(argparse.Namespace):
    VERSION = '1.0.0'

def parse_nest(arg):
    """
    Parses commandline arguments of nest

    :param arg: commandline arguments
    :type arg: String
    """
    
    # Add parser args
    parser = argparse.ArgumentParser('nest')
    parser.add_argument('--version', action='version', version=Argument.VERSION)
    parser.add_argument('-f', type=str, nargs='+', help='config file names', dest='config_files', action='store')
    parser.add_argument('-t', type=str, help='topology creation script', dest='topology_file', action='store')
    arguments = parser.parse_args(arg, namespace=Argument)
    
    # Run nest with given args 
    
    # Create topology
    if arguments.topology_file:
        create_topology(arguments.topology_file)

    # Run tests
    if arguments.config_files:
        run_tests(arguments.config_files)

### Functions for each arg option ###

def create_topology(topology_file):

    temp = engine.log_level
    engine.log_level = 1
    engine.exec_subprocess('python3 ' + topology_file)
    print(engine.LOGS[0]['stdout'])
    engine.log_level = temp

    stderr = engine.LOGS[0]['stderr']
    if stderr:
        print(stderr)

def run_tests(config_files):

    for config_file in config_files:
        statistics.parse_config(config_files)