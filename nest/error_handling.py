# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

##################################################
# This file contains all error checks and messages
##################################################

def type_verify(parameter_name, parameter, type_name, expected_types, supported_parameters=None):
    """
    Helper to verify parameters passed to the constructor

    :param parameter_name: Name of the parameter being verified
    :type parameter_name: string
    :param parameter: parameter to be verified
    :param type_name: Name of the type in string
    :type type_name: string
    :param expected_types: expected type of the parameter
    :type expected_types: type | list(type)
    :param supported_parameters: set of supported parameters
    :type supported_parameters: list{string}
    """

    # Convert expected_types to list if not list
    if type(expected_types) is not list:
        expected_types = [expected_types]

    is_expected = False
    for expected_type in expected_types:
        if type(parameter) is expected_type:
            is_expected = True

    if not is_expected:
        raise ValueError('{} is of type {}. Expected {}'.format(
            parameter_name, type(parameter), type_name))

    if supported_parameters is not None and parameter not in supported_parameters:
        raise ValueError('{} is not a supported {}'.format(
            parameter, parameter_name))
