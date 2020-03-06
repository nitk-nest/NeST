# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

from . import error_handling
from . import engine
from .id_generator import ID_GEN
import atexit

def print_logs():

    if engine.log_level > 0:
        for log in engine.LOGS:
            print('[COMMAND] ' + log['cmd'])
            print('[STDOUT] ' + log['stdout'])
            print('[STDERR] ' + log['stderr'])
            print('')

def set_log_level(log_level):

    error_handling.type_verify('log level', log_level, 'int', int)
    
    if 0 > log_level > 2:
        raise ValueError('Invalid value error')
    elif 1 <= log_level <= 2:
        engine.log_level = log_level
        atexit.register(lambda: print_logs())
        if log_level == 2:
            ID_GEN.disable_abstraction()