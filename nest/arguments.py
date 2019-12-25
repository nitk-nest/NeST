# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019 NITK Surathkal

import argparse


class Argument(argparse.Namespace):
    VERSION = '1.0.0'




parser = argparse.ArgumentParser('Network Stack Tester')
parser.add_argument('--version', action='version', version=Argument.VERSION)
#TODO: Add help


def parse(arg):
    """
    Parses commandline arguments

    :param arg: commandline arguments
    :type arg: String
    """
    arguments = parser.parse_args(arg, namespace=Argument)
    


