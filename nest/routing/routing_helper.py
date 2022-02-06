# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""
Helper class for routing
"""

import time
import logging
import importlib
from os import mkdir, kill, path, listdir
import atexit
from shutil import rmtree, chown
from signal import SIGTERM
from typing import List
from nest.exceptions import RequiredDependencyNotFound
from nest.input_validator.input_validator import input_validator
from nest.topology.id_generator import IdGen
from nest.routing.zebra import Zebra
from nest.routing.ldp import Ldp
from nest.topology_map import TopologyMap
from nest.user import User
from nest import config
from nest.topology import Node

logger = logging.getLogger(__name__)

# pylint:disable=too-few-public-methods
# pylint:disable=too-many-instance-attributes


class RoutingHelper:
    """
    Handles basic routing requirements for the topology.
    Either inherit this class or use `Zebra` and other protocols
    for better customizations

    Attributes
    ----------
    _module_map : dict
        map between protocol string and its module and class
    protocol : str
        routing protocol(one of ['rip', 'ospf', 'isis'])
    routers : List[Node]
        routers in the topology
    hosts : List[Node]
        hosts in the topology
    conf_dir : str
        path for config directory of daemons
    protocol_class : ABCMeta
        Protocol class which will later be instantiated
    """

    _module_map = {
        "ospf": ["nest.routing.ospf", "Ospf"],
        "rip": ["nest.routing.rip", "Rip"],
        "isis": ["nest.routing.isis", "Isis"],
    }

    @input_validator
    def __init__(
        self,
        protocol: str,
        hosts: List[Node] = None,
        routers: List[Node] = None,
        ldp_routers: List[Node] = None,
    ):
        """
        Constructor for RoutingHelper.
        The dynamic routing daemons will be run only on nodes with more than
        one interface. Specify `hosts` & `routers` parameters to override this.

        Parameters
        ----------
        protocol: str
            routing protocol to be run. One of [ospf, rip, isis]
        hosts: List[Node]
            List of hosts in the network. If `None`, considers the entire topology.
            Use this if your topology has disjoint networks
        routers: List[Node]
            List of routers in the network. If `None`, considers the entire topology.
            Use this if your topology has disjoint networks
        ldp_routers: List[Node]
            List of Routers which are to be used with mpls.
            Only enables ldp discovery on interfaces with mpls enabled
        """
        if protocol == "static":
            raise NotImplementedError(
                "Static routing is yet to be implemented. Use rip, ospf or isis"
            )
        if protocol not in ["rip", "ospf", "isis"]:
            raise ValueError(
                f"Supported routing protocols are rip, ospf and isis, "
                f"but got protocol {protocol}"
            )
        self.protocol = protocol

        # Validate hosts, routers and ldp_routers
        self._is_node_list("hosts", hosts)
        self._is_node_list("routers", routers)
        self._is_node_list("ldp_routers", ldp_routers)

        self.hosts = []
        self.routers = []
        if routers is None and hosts is None:
            all_nodes = TopologyMap.get_hosts() + TopologyMap.get_routers()
            for node in all_nodes:
                num_interfaces = len(node.interfaces)
                if num_interfaces == 1:
                    self.hosts.append(node)
                elif num_interfaces > 1:
                    self.routers.append(node)
        else:
            self.hosts = hosts
            self.routers = routers

        self.ldp_routers = ldp_routers if ldp_routers is not None else []
        self.conf_dir = None
        self.log_dir = None
        module_str, class_str = RoutingHelper._module_map[self.protocol]
        module = importlib.import_module(module_str)
        self.protocol_class = getattr(module, class_str)
        self.zebra_list = []
        self.protocol_list = []
        self.ldp_list = []

        atexit.register(self._clean_up)

    def populate_routing_tables(self):
        """
        Populate routing table using `self.protocol`
        """
        self._setup_default_routes()

        if self.protocol == "static":
            pass  # TODO: add static routing
        else:
            try:
                self._run_dyn_routing()
            except RequiredDependencyNotFound:
                return

    def _create_directory(self, dir_path):
        """
        Creates a quagga/frr owned directory at `dir_path`

        Parmeters
        ---------
        dir_path: path of the directory to be created

        """
        mkdir(dir_path)
        chown(dir_path, user=config.get_value("routing_suite"))

    def _create_conf_directory(self):
        """
        Creates a directory for holding routing related config
        and pid files.
        Override this to create directory at a location other than /tmp

        Returns
        -------
        str:
            path of the created directory
        """
        salt = config.get_value("routing_suite") + str(time.clock_gettime(0))
        dir_path = f"/tmp/{salt}-configs_{IdGen.topology_id}"
        self._create_directory(dir_path)
        return dir_path

    def _create_log_directory(self):
        """
        Creates a directory for holding routing log files.

        Returns
        -------
        str:
            path of the created directory
        """
        timestamp = time.strftime("%d-%m-%Y-%H:%M:%S")
        log_path = f"{config.get_value('routing_suite')}-logs_{timestamp}"
        self._create_directory(log_path)
        return log_path

    def _setup_default_routes(self):
        """
        Setup default routes in hosts
        """
        for host in self.hosts:
            host.add_route("DEFAULT", host.interfaces[0])

    def _run_dyn_routing(self):
        """
        Run zebra and `self.protocol`
        """
        logger.info("Running zebra and %s on routers", self.protocol)
        self.conf_dir = self._create_conf_directory()
        if config.get_value("routing_logs"):
            self.log_dir = self._create_log_directory()

        for router in self.routers:
            self._run_zebra(router)
            self._run_routing_protocol(router)
            if router in self.ldp_routers:
                self._run_ldp(router)
        self._check_for_convergence()

    def _run_zebra(self, router):
        """
        Create required config file and run zebra
        """
        zebra = Zebra(router.id, router.interfaces, self.conf_dir, log_dir=self.log_dir)
        zebra.create_basic_config()
        zebra.run()
        self.zebra_list.append(zebra)

    def _run_routing_protocol(self, router):
        """
        Create required config file and run `self.protocol`
        """
        protocol = self.protocol_class(
            router.id, router.interfaces, self.conf_dir, log_dir=self.log_dir
        )
        protocol.create_basic_config()
        protocol.run()
        self.protocol_list.append(protocol)

    def _run_ldp(self, router):
        """
        Create required config file and run ldp
        """
        mpls_interfaces = []
        for interface in router.interfaces:
            if interface.is_mpls_enabled():
                mpls_interfaces.append(interface)
        if len(mpls_interfaces) == 0:
            raise Exception("MPLS isn't enabled in any interface!")
        ldp = Ldp(router.id, mpls_interfaces, self.conf_dir, log_dir=self.log_dir)
        ldp.create_basic_config()
        ldp.run()
        self.ldp_list.append(ldp)

    def _check_for_convergence(self):
        """
        Wait for the routing protocol to converge.
        Override this for custom convergence check
        """
        logger.info("Waiting for %s to converge", self.protocol)
        interval = 2
        converged = False
        # Ping between hosts until convergence
        while not converged:
            time.sleep(interval)
            converged = True
            for i in range(len(self.hosts)):
                for j in range(i + 1, len(self.hosts)):
                    if not self.hosts[i].ping(
                        self.hosts[j].interfaces[0].address.get_addr(), verbose=False
                    ):
                        converged = False
                        break
                if not converged:
                    break

        logger.info("Routing completed")

    def _is_node_list(self, arg_name, node_list):
        """
        Checks if `node_list` is a list of Nodes.
        """
        if node_list is None:
            return
        for node in node_list:
            if isinstance(node, Node) is False:
                raise ValueError(
                    f"Some items in argument '{arg_name}' of method '{self.__init__.__qualname__}' "
                    f"are not derived from type '{Node.__name__}'"
                )

    def _clean_up(self):
        """
        Terminates routing daemons and deletes config files
        """
        # To preserve the routes, the daemons shouldn't be stopped
        # Frrouting doesn't seem to have an option to not flush the routes installed

        # Stop ldp processes
        for ldp in self.ldp_list:
            if path.isfile(ldp.pid_file):
                with open(ldp.pid_file, "r") as pid_file:
                    pid = int(pid_file.read())
                    try:
                        kill(pid, SIGTERM)
                    except ProcessLookupError:
                        pass

        # Stop zebra processes
        for zebra in self.zebra_list:
            if path.isfile(zebra.pid_file):
                with open(zebra.pid_file, "r") as pid_file:
                    pid = int(pid_file.read())
                    try:
                        kill(pid, SIGTERM)
                    except ProcessLookupError:
                        pass

        # Stop protocol processes
        for protocol in self.protocol_list:
            if path.isfile(protocol.pid_file):
                with open(protocol.pid_file, "r") as pid_file:
                    pid = int(pid_file.read())
                    try:
                        kill(pid, SIGTERM)
                    except ProcessLookupError:
                        pass

        # Delete config directory
        if path.isdir(self.conf_dir):
            rmtree(self.conf_dir)

        # Change ownership of log files to current user
        if self.log_dir is not None and path.isdir(self.log_dir):
            chown(self.log_dir, user=User.user_id, group=User.group_id)
            for file in listdir(self.log_dir):
                chown(
                    path.join(self.log_dir, file),
                    user=User.user_id,
                    group=User.group_id,
                )
