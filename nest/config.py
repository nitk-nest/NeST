# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

""" APIs to process config files """

import os
import json
import logging
from nest.logging_helper import update_nest_logger

logger = logging.getLogger(__name__)

__DEFAULT_VALUE = {}
__DEFAULT_PATH = [
    "/etc/nest-config.json",
    os.path.expanduser("~") + "/.nest-config.json",
    os.getcwd() + "/nest-config.json",
]


def import_default_config():
    """
    Reads `config.json` file from necessary specified file locations and converts it into a string

    Returns
    -------
    dict
        The information in the default config file as a python dictionary
    """
    # Having it as a private, global variable prevents users from directly accessing it
    # pylint: disable=global-statement

    global __DEFAULT_VALUE
    with open(
        os.path.realpath(os.path.dirname(__file__)) + "/config.json", "r"
    ) as json_file:
        data = json.load(json_file)

    __DEFAULT_VALUE = data


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
    if parameter in __DEFAULT_VALUE:
        __DEFAULT_VALUE[parameter] = value
    else:
        logger.error("The given parameter %s does not exist", parameter)
        return

    _post_set_value(parameter, value)


def _post_set_value(parameter, value):
    """
    Called after setting a config value. Used for executing
    parameter specific code.

    Attributes
    ----------
    parameter: str
        The parameter's value which has to be changed
    value: str
        The value to which the parameter has to be changed to
    """

    if parameter == "log_level":
        update_nest_logger(value)


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
    if parameter in __DEFAULT_VALUE:
        return __DEFAULT_VALUE[parameter]
    # If it belonged to none of them
    logger.error("The given parameter %s does not exist", parameter)
    return None


def import_custom_config(path):
    """
    Overwrites the current value of config parameters with the values
    from the JSON in the given path

    Attributes
    ----------
    path: str
        The path in which the json file
    """
    # pylint: disable=too-many-branches
    with open(path, "r") as json_file:
        data = json.load(json_file)
    for parameter in data:
        if parameter in __DEFAULT_VALUE:
            __DEFAULT_VALUE[parameter] = data[parameter]
            _post_set_value(parameter, data[parameter])
        else:
            logger.error("The given parameter %s does not exist", parameter)


def search_config_files():
    """
    Searches a few predifined locations for a config files
    """

    # The ones called later, might overwrite the previous calls
    for i in __DEFAULT_PATH:
        if os.path.isfile(os.path.abspath(i)):
            import_custom_config(os.path.abspath(i))
