# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

""" API's to process config files """

import os
import json
import logging

default_value = {'topology': {}, 'experiment': {}, 'engine': {}}

def import_default_config():
    """
    Reads `config.json` file from necessary specified file locations and converts it into a string

    Returns
    -------
    dict
        The information in the default config file as a python dictionary
    """
    with open(os.path.realpath(os.path.dirname(__file__)) + '/config.json', 'r') as json_file:
        data = json.load(json_file)
        # print(data)
        return data

def set_value(parameter, value):
    """
    Changes the default values only for that program

    Attributes
    ----------
    parameter: str
        The parameter's value which has to be changed
    value: str
        The value to which the parameter has to be changed to
    """
    if parameter in default_value:
        default_value[parameter] = value
    elif parameter in default_value['topology']:
        default_value['topology'][parameter] = value
    elif parameter in default_value['experiment']:
        default_value['experiment'][parameter] = value
    elif parameter in default_value['engine']:
        default_value['engine'][parameter] = value
    else:
        logging.error('The given parameter %s does not exist', parameter)

def get_value(parameter):
    """
    Returns the default value of the parameter

    Attributes
    ----------
    parameter: str
        The parameter whose value is to be returned

    Returns
    -------
    str
        The value of the parameter
    """
    if parameter in default_value:
        return default_value[parameter]
    elif parameter in default_value['topology']:
        return default_value['topology'][parameter]
    elif parameter in default_value['experiment']:
        return default_value['experiment'][parameter]
    elif parameter in default_value['engine']:
        return default_value['engine'][parameter]
    else:
        logging.error('The given parameter %s does not exist', parameter)
