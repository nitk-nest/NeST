# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Stores user information"""

# pylint: disable=too-few-public-methods
class User:
    """
    User info (user id and group id) stored here.

    Attributes
    ----------
    user_id : int
        User id of user
    group_id : int
        Group id of user

    """

    user_id = -1
    group_id = -1

    def __init__(self, user_id, group_id):
        """
        Initialize user info.

        Parameters
        ----------
        user_id : int
        group_id : int

        """
        User.user_id = user_id
        User.group_id = group_id
