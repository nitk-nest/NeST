# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""
Helped class for routing
"""

import time
import logging
import importlib
from nest.topology.id_generator import IdGen
from nest.routing.zebra import Zebra
from nest.topology_map import TopologyMap
from nest.engine.quagga import create_quagga_directory

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
class RoutingHelper:
    """
    Handles basic routing requirements for the topology.
    Either inherit this class or use `Zebra` and other protocols
    for better customizations

    Attributes
    ----------
    module_map : dict
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

    module_map = {
        'ospf': ['nest.routing.ospf', 'Ospf']
    }

    def __init__(self, protocol):
        self.protocol = protocol
        self.routers = TopologyMap.get_routers()
        self.hosts = TopologyMap.get_hosts()
        self.conf_dir = None
        module_str, class_str = RoutingHelper.module_map[self.protocol]
        module = importlib.import_module(module_str)
        self.protocol_class = getattr(module, class_str)

    def _create_quagga_directory(self, path):
        """
        Creates a directly for holding quagga related config
        and pid files

        Parameters
        ----------
        path : str
            config directory path. Generally /tmp
        """
        dir_path = f'{path}/{IdGen.topology_id}_quagga-configs'
        create_quagga_directory(dir_path)
        return dir_path

    def populate_routing_tables(self):
        """
        Populate routing table using `self.protocol`
        """

        self.setup_default_routes()

        if self.protocol == 'static':
            pass  # TODO: add static routing
        else:
            self.run_quagga()

    def setup_default_routes(self):
        """
        Setup default routes in hosts
        """
        for host in self.hosts:
            host.add_route('DEFAULT', host.interfaces[0])

    def run_quagga(self):
        """
        Run zebra and `self.protocol`
        """
        logger.info('Running zebra and %s in routers', self.protocol)
        self.conf_dir = self._create_quagga_directory('/tmp')
        for router in self.routers:
            self.run_zebra(router)
            self.run_routing_protocol(router)
        self.check_for_convergence()

    def run_zebra(self, router):
        """
        Create requird config file and run zebra
        """
        zebra = Zebra(router.id, router.interfaces, self.conf_dir)
        zebra.create_basic_config()
        zebra.run()

    def run_routing_protocol(self, router):
        """
        Create requird config file and run `self.protocol`
        """
        protocol = self.protocol_class(router.id, router.interfaces, self.conf_dir)
        protocol.create_basic_config()
        protocol.run()

    def check_for_convergence(self):
        """
        Wait for the routing protocol to converge.
        Override this for custom convergence check
        """
        logger.info('Waiting for %s to converge', self.protocol)
        interval = 2
        converged = False
        #Ping between hosts until convergence
        while not converged:
            time.sleep(interval)
            converged = True
            for i in range(len(self.hosts)):
                for j in range(i+1, len(self.hosts)):
                    if not self.hosts[i].ping(self.hosts[j].interfaces[0].address.get_addr()
                        , verbose=False):
                        converged = False
                        break
                if not converged:
                    break

        logger.info('Routing compeleted')
