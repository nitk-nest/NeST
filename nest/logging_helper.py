# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Helper function for logging"""

import logging
import re

# See: https://stackoverflow.com/a/35804945
def add_logging_level(level_name, level_num, method_name=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not method_name:
        method_name = level_name.lower()

    if hasattr(logging, level_name):
        raise AttributeError(f"{level_name} already defined in logging module")
    if hasattr(logging, method_name):
        raise AttributeError(f"{method_name} already defined in logging module")
    if hasattr(logging.getLoggerClass(), method_name):
        raise AttributeError(f"{method_name} already defined in logger class")

    def log_for_level(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            # pylint: disable=protected-access
            self._log(level_num, message, args, **kwargs)

    def log_to_root(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    logging.addLevelName(level_num, level_name)
    setattr(logging, level_name, level_num)
    setattr(logging.getLoggerClass(), method_name, log_for_level)
    setattr(logging, method_name, log_to_root)


def get_trace_filehandler():
    """
    Creates and returns a file handler for logging engine commands
    """
    filehandler = logging.FileHandler("commands.sh", "w")
    # pylint: disable=no-member
    filehandler.setLevel(logging.TRACE)
    formatter = logging.Formatter("%(message)s")
    filehandler.setFormatter(formatter)
    filehandler.addFilter(lambda record: record.levelno == logging.TRACE)

    return filehandler


def update_nest_logger(level):
    """
    Update top logger when log level is updated via config

    Parameters
    ----------
    level: str
        log level from config
    """
    nest_logger = logging.getLogger(
        __name__.split(".", maxsplit=1)[0]
    )  # get the root's child logger
    nest_logger.setLevel(level)  # Update logger level
    # Update handler level
    nest_handler = nest_logger.handlers[0]
    nest_handler.setLevel(level)
    # pylint: disable=no-member
    if level == "TRACE" and not any(
        handler.level == logging.TRACE and handler is logging.FileHandler
        for handler in nest_logger.handlers
    ):  # Avoid adding multiple trace filehandlers
        nest_logger.addHandler(get_trace_filehandler())


# pylint: disable=too-few-public-methods
class DuplicateFilter(logging.Filter):
    """
    Super class for duplicate filter
    """

    def __init__(self):
        super().__init__()
        self.messages = set()
        self.filter_pat = r".*"

    def filter(self, record):
        """
        Checks whether log message is already
        logged and adds it to the current set of
        logged message accordingly
        """
        log_message = record.getMessage()

        if log_message in self.messages:
            return 0

        if re.match(self.filter_pat, log_message) is not None:
            self.messages.add(log_message)
        return 1


# pylint: disable=too-few-public-methods
class DepedencyCheckFilter(logging.Filter):
    """
    Filters duplicate depedency missing logs.
    """

    def __init__(self):
        super().__init__()
        self.messages = set()

        # Assuming the depedency error is of the form "{depedency} not found".
        self.filter_pat = r"(\w|\d|-|_)+ not found\."


class DuplicateRoutingLogsFilter(DuplicateFilter):
    """
    Filters duplicate "quagga/frr logging enabled" logs
    """

    def __init__(self):
        super().__init__()
        self.messages = set()

        # Assuming the log is of the form
        # "{frr/quagga} logging enabled. Log files can found in {dir} directory".
        # pylint: disable=line-too-long
        self.filter_pat = r"(quagga|frr) logging enabled\. Log files can found in (\w|\d|-|_|:)+ directory"
