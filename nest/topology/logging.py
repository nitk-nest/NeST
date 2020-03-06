# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

from . import error_handling
from .. import engine
from .id_generator import ID_GEN
import atexit

def _print_logs():
    """
    Print logs provided by engine.LOGS
    """

    if engine.log_level > 0:
        for log in engine.LOGS:
            print('[COMMAND] ' + log['cmd'])
            print('[STDOUT] ' + log['stdout'])
            print('[STDERR] ' + log['stderr'])
            print('')

def set_log_level(log_level):
    """
    Set log level
    0: No logging (default)
    1: Log the iproute2 commands run
    2: 1 + use user given names for iproute2 commands 

    :param ns_name: The name of the namespace to be created
    :type ns_name: string
    """

    error_handling.type_verify('log level', log_level, 'int', int)
    
    if 0 > log_level > 2:
        raise ValueError('Invalid value error')
    elif 1 <= log_level <= 2:
        engine.log_level = log_level
        atexit.register(lambda: _print_logs())
        if log_level == 2:
            ID_GEN.disable_unique_id()