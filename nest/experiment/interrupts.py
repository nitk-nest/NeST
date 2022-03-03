# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""
Helper methods to handle interrupts from the user.

For eg., KeyboardInterrupt
"""

import functools
import logging

logger = logging.getLogger(__name__)


def handle_keyboard_interrupt(func):
    """
    Decorator for handling keyboard interrupt.
    It is assumed that this decorator is used in subprocesses.
    (the debug message is formulated accordingly)
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except KeyboardInterrupt:
            logger.debug(
                "Running %s: Received KeyboardInterrupt, "
                "hence shutting down the process gracefully.",
                func.__qualname__,
            )
        return result

    return wrapper
