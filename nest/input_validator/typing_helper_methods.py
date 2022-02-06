# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""
Helper methods for handling types from typing module.

NOTE: This module uses private members of typing module
for backward compatibility with python 3.7 and older versions.
"""

import typing


def is_optional(field):
    """
    Returns if the `field` type is of Optional type

    Parameters
    ----------
    field: typing
        The type to be checked

    Returns
    -------
    bool
        Returns True if `field` is optional
    """
    if hasattr(field, "__args__") and hasattr(field, "__origin__"):
        if (
            # pylint: disable=comparison-with-callable
            field.__origin__ == typing.Union
            and len(field.__args__) == 2
            and field.__args__[-1] is type(None)
        ):
            return True

    return False


def get_inner_type_of_optional_field(field):
    """
    Get inner type inside optional field
    """
    return field.__args__[0]


def is_list(field):
    """
    Checks if `field` type is a list.
    """
    if hasattr(field, "__args__") and hasattr(field, "__origin__"):
        if field.__origin__ == list:
            return True
    return False
