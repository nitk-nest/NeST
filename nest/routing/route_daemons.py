# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""
Base class for Routing daemons.
"""

from abc import ABC, abstractmethod
import io
import logging
import shutil
from nest.engine.util import is_dependency_installed
from nest.logging_helper import DuplicateFilter
from nest.engine.dynamic_routing import chown_to_daemon


class RoutingDaemonBase(ABC):
    """
    Abstract class for Dynamic routing related processes.
    This class should be inherited for adding other daemons

    Use `add_to_config` to sequentially add daemon related commands
    for the config files.

    Call `create_config_command` to actually create the file on disk

    Finally call `run` to run the daemon. Uses the above created config file.

    Note:
    (i): If you're using `RoutingHelper`, config files are created at the /tmp
    directory.
    (ii): Daemons may not work as expected if a config file is not created

    Attributes
    ----------
    conf: file-like
        In memory stream to temporarily hold configuration
    router_ns_id : str
        Router namespace id
    daemon : str
        daemon to run(one of ['zebra', 'ospf', 'isis'])
    conf_file : str
        config file path
    pid_file : str
        pid file path for the daemon process
    interfaces : List[Interface]
        interfaces present in the router
    """

    def __init__(self, router_ns_id, interfaces, daemon, conf_dir):
        self.logger = logging.getLogger(__name__)
        if not any(isinstance(filter, DuplicateFilter) for filter in self.logger.filters):
            # Duplicate filter is added to avoid logging of same error
            # message incase any of the routing daemon is not installed
            self.logger.addFilter(DuplicateFilter())

        if not is_dependency_installed(daemon):
            self.handle_dependecy_error()

        self.conf = io.StringIO()
        self.router_ns_id = router_ns_id
        self.daemon = daemon
        self.conf_file = f"{conf_dir}/{self.router_ns_id}_{daemon}.conf"
        self.pid_file = f"{conf_dir}/{self.router_ns_id}_{daemon}.pid"
        self.interfaces = interfaces
        self.ipv6 = interfaces[0].address.is_ipv6()

    @abstractmethod
    def create_basic_config(self):
        """
        Created minimum configuration for `daemon`
        """

    @abstractmethod
    def run(self):
        """
        Run the `daemon` along with its config file
        """

    def add_to_config(self, command):
        """
        Add a line to `self.conf`

        Parameters
        ---------
        command : str
            command to add to config file
        """
        self.conf.write(f"{command}\n")

    def create_config(self):
        """
        Creates config file on disk from `self.conf`
        """
        with open(self.conf_file, "w") as conf:
            chown_to_daemon(self.conf_file)
            self.conf.seek(0)
            shutil.copyfileobj(self.conf, conf)

    def handle_dependecy_error(self):
        """
        Default error when routing daemon is not present
        """
        self.logger.error('%s not found. Routes may not be added properly', self.daemon)
