# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""
Helper class for routing
"""

import time
import logging
import importlib
from os import mkdir, kill, path
import atexit
from shutil import rmtree
from signal import SIGTERM
from nest.topology.id_generator import IdGen
from nest.routing.zebra import Zebra
from nest.topology_map import TopologyMap
from nest.engine.quagga import chown_quagga

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# pylint:disable=too-few-public-methods


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
        routing protocol(one of['ospf'])
    routers : List[Node]
        routers in the topology
    hosts : List[Node]
        hosts in the topology
    conf_dir : str
        path for quagga config directory
    protocol_class : ABCMeta
        Protocol class which will later be instantiated
    """

    _module_map = {
        'ospf': ['nest.routing.ospf', 'Ospf'],
        'rip': ['nest.routing.rip', 'Rip'],
        'isis': ['nest.routing.isis', 'Isis']
    }

    def __init__(self, protocol='static', hosts=None, routers=None):
        """
        Constructor for RoutingHelper

        Parameters
        ----------
        protocol: str
            routing protocol to be run. One of [ospf, rip]
        hosts: List[Node]
            List of hosts in the network. If `None`, considers the entire topology.
            Use this if your topology has disjoint networks
        routers: List[Node]
            List of routers in the network. If `None`, considers the entire topology.
            Use this if your topology has disjoint networks
        """
        if protocol == 'static':
            raise NotImplementedError(
                'Static routing is yet to be implemented. Use rip or ospf')
        self.protocol = protocol
        self.routers = TopologyMap.get_routers() if routers is None else routers
        self.hosts = TopologyMap.get_hosts() if hosts is None else hosts
        self.conf_dir = None
        module_str, class_str = RoutingHelper._module_map[self.protocol]
        module = importlib.import_module(module_str)
        self.protocol_class = getattr(module, class_str)
        self.zebra_list = []
        self.protocol_list = []

        atexit.register(self._clean_up)

    def populate_routing_tables(self):
        """
        Populate routing table using `self.protocol`
        """
        self._setup_default_routes()

        if self.protocol == 'static':
            pass  # TODO: add static routing
        else:
            self._run_quagga()

    def _create_quagga_directory(self):
        """
        Creates a directly for holding Quagga related config
        and pid files.
        Override this to create directory at a location other than /tmp

        Returns
        -------
        str:
            path of the created directory
        """
        dir_path = f'/tmp/quagga-configs_{IdGen.topology_id}'
        mkdir(dir_path)
        chown_quagga(dir_path)
        return dir_path

    def _setup_default_routes(self):
        """
        Setup default routes in hosts
        """
        for host in self.hosts:
            host.add_route('DEFAULT', host.interfaces[0])

    def _run_quagga(self):
        """
        Run zebra and `self.protocol`
        """
        logger.info('Running zebra and %s on routers', self.protocol)
        self.conf_dir = self._create_quagga_directory()
        for router in self.routers:
            self._run_zebra(router)
            self._run_routing_protocol(router)
        self._check_for_convergence()

    def _run_zebra(self, router):
        """
        Create required config file and run zebra
        """
        zebra = Zebra(router.id, router.interfaces, self.conf_dir)
        zebra.create_basic_config()
        zebra.run()
        self.zebra_list.append(zebra)

    def _run_routing_protocol(self, router):
        """
        Create required config file and run `self.protocol`
        """
        protocol = self.protocol_class(
            router.id, router.interfaces, self.conf_dir)
        protocol.create_basic_config()
        protocol.run()
        self.protocol_list.append(protocol)

    def _check_for_convergence(self):
        """
        Wait for the routing protocol to converge.
        Override this for custom convergence check
        """
        logger.info('Waiting for %s to converge', self.protocol)
        interval = 2
        converged = False
        # Ping between hosts until convergence
        while not converged:
            time.sleep(interval)
            converged = True
            for i in range(len(self.hosts)):
                for j in range(i+1, len(self.hosts)):
                    if not self.hosts[i].ping(self.hosts[j].interfaces[0].address.get_addr(),
                                              verbose=False):
                        converged = False
                        break
                if not converged:
                    break

        logger.info('Routing completed')
        self._clean_up()

    def _clean_up(self):
        """
        Terminates Quagga daemons and deletes config files
        """

        # Stop zebra processes
        for zebra in self.zebra_list:
            if path.isfile(zebra.pid_file):
                with open(zebra.pid_file, 'r') as pid_file:
                    pid = int(pid_file.read())
                kill(pid, SIGTERM)

        # Stop protocol processes
        for protocol in self.protocol_list:
            if path.isfile(protocol.pid_file):
                with open(protocol.pid_file, 'r') as pid_file:
                    pid = int(pid_file.read())
                kill(pid, SIGTERM)

        # Delete config directory
        if path.isdir(self.conf_dir):
            rmtree(self.conf_dir)
