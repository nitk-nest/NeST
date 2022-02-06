# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""
Helper classes and methods for client-side input validation.
"""

import typing
import functools
import logging
from builtins import isinstance
from inspect import getfullargspec
from .typing_helper_methods import (
    get_inner_type_of_optional_field,
    is_list,
    is_optional,
)

logger = logging.getLogger(__name__)


def input_validator(func):
    """
    Decorator to validate the input provided by the user for function `func`.
    This also typecasts the parameters of `func` as per the provided
    type hints in the function.

    Each parameter in `func` is expected to have a type hint. Type hints
    are necessary for input validation. If type hint is not provided for a
    parameter, then the input for the parameter will not be validated and
    type casted.

    Note: Default values of parameters are not validated.

    Parameters
    ----------
    func: Function
        Decorated function whose types are validated

    Returns
    -------
    func(*args, **kwargs)
        If all args are valid, then calls the decorated function with
        typecasted parameters.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        argspec = getfullargspec(func)

        # Forward references type hints:
        # https://www.python.org/dev/peps/pep-0563/#resolving-type-hints-at-runtime
        annotations = typing.get_type_hints(func)

        casted_args = []
        casted_kwargs = {}

        for (arg_name, arg_value) in zip(argspec.args, args):
            casted_arg_value = arg_value
            if arg_name in annotations:
                casted_arg_value = validate_input_and_cast(
                    func.__qualname__, arg_name, arg_value, annotations[arg_name]
                )
            else:
                logger.debug(
                    "Parameter %s of function %s does not have a type hint",
                    arg_name,
                    func.__qualname__,
                )
            casted_args.append(casted_arg_value)

        # Default values are not checked here, it is assumed that correct
        # values are passed for default parameters
        for kwarg_name in kwargs:
            kwarg_value = kwargs[kwarg_name]
            casted_kwarg_value = kwarg_value
            if kwarg_name in annotations:
                casted_kwarg_value = validate_input_and_cast(
                    func.__qualname__, kwarg_name, kwarg_value, annotations[kwarg_name]
                )
            else:
                logger.debug(
                    "Parameter %s of function %s does not have a type hint",
                    kwarg_name,
                    func.__qualname__,
                )
            casted_kwargs[kwarg_name] = casted_kwarg_value

        return func(*casted_args, **casted_kwargs)

    return wrapper


def validate_input_and_cast(func_name, arg_name, arg_value, expected_type):
    """
    Validate input `arg_value` provided by user for parameter `arg_name`
    of function `func_name`. The type of `arg_value` is expected to be
    `expected_type`.

    Returns the `arg_value` if it is of expected_type. If the `arg_value`
    can be typecasted to `expected_type`, then the type casted value is
    returned. Else TypeError exception is raised.

    Parameters
    ----------
    func_name: string
        Name of the function whose parameters are being validated
    arg_name: string
        Name of the parameter being validated.
    arg_value: object
        The input value for the parameter given by the client/user.
    expected_type: type
        The expected type of `arg_value`. Forward referencing is supported:
        https://www.python.org/dev/peps/pep-0484/#forward-references.
        So, `expected_type` can be a string which evalautes to a type.

    Returns
    -------
    object
        Return true if `client__input` is of type `expected_type`.
        Else returns false.
    """
    if is_optional(expected_type):
        # For optional field, check if arg_value is None.
        if arg_value is None:
            return arg_value

        # Strip out the optional field tag, for compatibility with
        # older python versions (python 3.7)
        expected_type = get_inner_type_of_optional_field(expected_type)

    if is_list(expected_type):
        # For list, we only validate that `arg_value` is a list.
        # We do not validate the inner contents of the list.
        if isinstance(arg_value, list):
            return arg_value

        raise TypeError(
            f"Expected type of argument '{arg_name}' in method '{func_name}' is List. "
            f"But got input '{arg_value}' of type {type(arg_value)}"
        )

    if isinstance(arg_value, expected_type):
        return arg_value

    if hasattr(expected_type, "allowed_type_cast"):
        for casting_type in expected_type.allowed_type_cast():
            if isinstance(arg_value, casting_type):
                try:
                    return expected_type(arg_value)
                except ValueError as error:
                    raise TypeError(
                        f"For argument '{arg_name}' in method '{func_name}', "
                        f"converting '{arg_value}' to type {expected_type.__name__} failed.\n"
                        f"Please see the previous exception to know why the conversion failed."
                    ) from error

    raise TypeError(
        f"Expected type of argument '{arg_name}' in method '{func_name}' is {expected_type}. "
        f"But got input '{arg_value}' of type {type(arg_value)}"
    )
