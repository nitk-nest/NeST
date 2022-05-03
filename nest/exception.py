# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""
The base exception for all exceptions created in NeST
"""


class NestBaseException(Exception):
    """
    Base exception for all exceptions created in NeST
    """


class RequiredDependencyNotFound(Exception):
    """
    Raised when a depedency required for a experiment/topology
    is not installed.
    """

    def __init__(self, message="Depedency required for this program is not installed"):
        self.message = message
        super().__init__(self.message)


class DelayNotSetInInterface(NestBaseException):
    """
    Raised when delay is not set on the interface.
    """

    def __init__(
        self,
        message="Delay must be set on the interface before set_packet_reorder method is used."
        "\nPlease set delay first using set_delay or set_attributes methods",
    ):

        self.message = message
        super().__init__(self.message)


class DistributionOptionError(NestBaseException):
    """
    Raised when the delay distribution is not set properly
    """
