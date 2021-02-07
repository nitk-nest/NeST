# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2021 NITK Surathkal
"""
Custom exceptions
"""


class RequiredDependencyNotFound(Exception):
    """
    Raised when a depedency required for a experiment/topology
    is not installed.
    """

    def __init__(self, message="Depedency required for this program is not installed"):
        self.message = message
        super().__init__(self.message)
