# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import argparse
from . import statistics
from . import engine

class Argument(argparse.Namespace):
    VERSION = '1.0.0'

class RunTests(argparse.Action):
    """
    An action class which calls `parse_config` to 
    parse and run configuration files
    """

    def __call__(self, parser, namespace, values, option_string):
        statistics.parse_config(values)
        setattr(namespace, self.dest, values)

class CreateTopology(argparse.Action):
    """
    Action to create topology as per topology file
    """

    def __call__(self, parser, namespace, value, option_string):
        engine.exec_subprocess('python3 ' + value)
        setattr(namespace, self.dest, value)

def parse(arg):
    """
    Parses commandline arguments

    :param arg: commandline arguments
    :type arg: String
    """
    parser = argparse.ArgumentParser('Network Stack Tester')
    parser.add_argument('--version', action='version', version=Argument.VERSION)
    parser.add_argument('-f', type=str, nargs='+', help='config file names', dest='config_files', action=RunTests)
    parser.add_argument('-t', type=str, help='topology creation script', dest='topology_file', action=CreateTopology)
    arguments = parser.parse_args(arg, namespace=Argument)
