# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# Store user information

class User():
    """
    User info like user_id and group_id stored here.
    """

    user_id = 0
    group_id = 0

    def __init__(self, user_id, group_id):
        """
        Initialize user info

        :param user_id: User ID
        :type user_id: int
        :param group_id: User Group ID
        :type group_id: int
        """
        
        User.user_id = user_id
        User.group_id = group_id

    @staticmethod
    def get_user_id():
        """
        Getter for user id
        """

        return User.user_id

    @staticmethod
    def get_group_id():
        """
        Getter for group id
        """

        return User.group_id
