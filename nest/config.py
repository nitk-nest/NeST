# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

""" APIs to process config files """

import os
import json
import logging

logger = logging.getLogger(__name__)

__DEFAULT_VALUE = {"engine": {}, "experiment": {}, "routing": {}, "topology": {}}


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
    if parameter in __DEFAULT_VALUE["engine"]:
        __DEFAULT_VALUE["engine"][parameter] = value
    elif parameter in __DEFAULT_VALUE["experiment"]:
        __DEFAULT_VALUE["experiment"][parameter] = value
    elif parameter in __DEFAULT_VALUE["routing"]:
        __DEFAULT_VALUE["routing"][parameter] = value
    elif parameter in __DEFAULT_VALUE["topology"]:
        __DEFAULT_VALUE["topology"][parameter] = value
    elif parameter in __DEFAULT_VALUE:
        __DEFAULT_VALUE[parameter] = value
    else:
        logger.error("The given parameter %s does not exist", parameter)


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
    if parameter in __DEFAULT_VALUE["engine"]:
        return __DEFAULT_VALUE["engine"][parameter]
    if parameter in __DEFAULT_VALUE["experiment"]:
        return __DEFAULT_VALUE["experiment"][parameter]
    if parameter in __DEFAULT_VALUE["routing"]:
        return __DEFAULT_VALUE["routing"][parameter]
    if parameter in __DEFAULT_VALUE["topology"]:
        return __DEFAULT_VALUE["topology"][parameter]
    if parameter in __DEFAULT_VALUE:
        return __DEFAULT_VALUE[parameter]

    # If it belonged to none of them
    logger.error("The given parameter %s does not exist", parameter)
    return "The given parameter %s does not exist"


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
    if "engine" in data:
        for parameter in data["engine"]:
            if parameter in __DEFAULT_VALUE["engine"]:
                __DEFAULT_VALUE["engine"][parameter] = data["engine"][parameter]
            else:
                logger.error("The given parameter %s does not exist", parameter)
    if "experiment" in data:
        for parameter in data["experiment"]:
            if parameter in __DEFAULT_VALUE["experiment"]:
                __DEFAULT_VALUE["experiment"][parameter] = data["experiment"][parameter]
            else:
                logger.error("The given parameter %s does not exist", parameter)
    if "routing" in data:
        for parameter in data["routing"]:
            if parameter in __DEFAULT_VALUE["routing"]:
                __DEFAULT_VALUE["routing"][parameter] = data["routing"][parameter]
            else:
                logger.error("The given parameter %s does not exist", parameter)
    if "topology" in data:
        for parameter in data["topology"]:
            if parameter in __DEFAULT_VALUE["topology"]:
                __DEFAULT_VALUE["topology"][parameter] = data["topology"][parameter]
            else:
                logger.error("The given parameter %s does not exist", parameter)
    for parameter in data:
        if parameter in __DEFAULT_VALUE.keys():
            if not isinstance(__DEFAULT_VALUE[parameter], dict):
                __DEFAULT_VALUE[parameter] = data[parameter]
        else:
            logger.error("The given parameter %s does not exist", parameter)
