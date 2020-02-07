# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import argparse
from .statistics import parse_config


class Argument(argparse.Namespace):
    VERSION = '1.0.0'

class RunTests(argparse.Action):
    """
    An action class which calls `parse_config` to 
    parse and run configuration files
    """

    def __call__(self, parser, namespace, values, option_string):
        parse_config(values)
        setattr(namespace, self.dest, values)


def parse(arg):
    """
    Parses commandline arguments

    :param arg: commandline arguments
    :type arg: String
    """
    parser = argparse.ArgumentParser('Network Stack Tester')
    parser.add_argument('--version', action='version', version=Argument.VERSION)
    parser.add_argument('-f', type=str, nargs='+', help='config file names', dest='config_files', action=RunTests)
    arguments = parser.parse_args(arg, namespace=Argument)
