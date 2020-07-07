# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# API related to nodes in topology
from .address import Address
from .. import engine
from .. import error_handling
from .id_generator import ID_GEN
from ..topology_map import TopologyMap


class Namespace:
    """
    Base namespace class which is inherited by `Node` and `Router` classes
    """

    def __init__(self, ns_name=''):
        """
        Constructor to initialize an unique id, name and a empty
        list of interfaces for the namespace

        :param ns_name: The name of the namespace to be created
        :type ns_name: string
        """

        if(ns_name != ''):
            self.name = ns_name
            self.id = ID_GEN.get_id(ns_name)

            engine.create_ns(self.id)
        else:
            # TODO: We should probably raise an error here.
            self.id = 'default'

        # Add namespace to TopologyMap
        TopologyMap.add_namespace(self.get_id(), self.get_name())

        # Initialize an empty list of interfaces to keep track of interfaces on it
        self.interface_list = []

    def is_default(self):
        """
        Checks if the namespace is same as the default
        namespace.
        """

        if self.id == 'default':
            return True
        else:
            return False

    def get_id(self):
        """
        Get the (unique) id of the namespace
        """

        return self.id

    def get_name(self):
        """
        Get the (user-assigned) name of the namespace
        """

        return self.name

    def add_route(self, dest_addr, via_interface, next_hop_addr=''):
        """
        Adds a route to the routing table of the namespace with
        the given parameters

        :param dest_addr: Destination ip address of the namespace or DEFAULT for all adresses
        :type dest_addr: Address or string
        :param via_interface: interface on the namespace used to route
        :type via_interface: Interface
        :param next_hop_address: ip address of the next hop router
        :type next_hop_address: Address or string
        """

        if type(dest_addr) == str:
            dest_addr = Address(dest_addr)

        if next_hop_addr != '':
            if type(next_hop_addr) == str:
                next_hop_addr = Address(next_hop_addr)
        else:
            next_hop_addr = via_interface.get_pair().get_address()

        dest_addr_str = ''
        if dest_addr.is_subnet():
            dest_addr_str = dest_addr.get_addr()
        else:
            dest_addr_str = dest_addr.get_addr(with_subnet=False)

        engine.add_route(self.id, dest_addr_str, next_hop_addr.get_addr(with_subnet=False),
                         via_interface.get_id())

    def _add_interface(self, interface):
        """
        Adds an interface to the namespace

        :param interface: Interface to be added to the namespace
        :type interface: Interface
        """

        self.interface_list.append(interface)
        interface._set_namespace(self)
        engine.add_int_to_ns(self.get_id(), interface.get_id())

        # Add interface to TopologyMap
        TopologyMap.add_interface(
            self.get_id(), interface.get_id(), interface.get_name())

    def configure_tcp_param(self, param, value):
        """
        Configures tcp parameretes available at /proc/sys/net/ipv4/tcp_*.
        Eg. window_scaling, wmem, ecn, etc.

        :param param: tcp parameter to be configured
        :type param: string
        :param value: value of the parameter
        :type param: string
        """

        engine.configure_kernel_param(
            self.get_id(), 'net.ipv4.tcp_', param, value)

    def configure_udp_param(self, param, value):
        """
        Configures udp parameretes available at /proc/sys/net/ipv4/udp_*.
        They are early_demux, l3mdev_accept, mem, rmem_min, wmem_min
        
        :param param: udp parameter to be configured
        :type param: string
        :param value: value of the parameter
        :type param: string
        """

        engine.configure_kernel_param(
            self.get_id(), 'net.ipv4.udp_', param, value)

    def read_tcp_param(self, param):
        """
        read tcp_parameters available at /proc/sys/net/ipv4/tcp_*
        Eg. window_scaling, wmem, ecn, etc.

        :param param: tcp parameter to be read
        :type param: string
        :returns string -- value of the tcp parameters
        """

        return engine.read_kernel_param(self.get_id(), 'net.ipv4.tcp_', param)

    def read_udp_param(self, param):
        """
        read tcp_parameters available at /proc/sys/net/ipv4/udp_*
        They are early_demux, l3mdev_accept, rmem_min, wmem_min

        :param param: udp parameter to be read
        :type param: string
        :returns string -- value of the udp parameters
        """

        return engine.read_kernel_param(self.get_id(), 'net.ipv4.udp_', param)

    def ping(self, destination_address, verbose=True):
        """
        Ping from current namespace to destination address
        if there is a route.
        To check if the topology is correctly implemented.

        :param destination_address: Address to ping to
        :type destination_address: string/Address
        :param verbose: If should print ping success/failure details
        :type verbose: boolean
        :return: Success of ping
        :r_type: boolean
        """

        if type(destination_address) == str:
            destination_address = Address(destination_address)

        status = engine.ping(
            self.id, destination_address.get_addr(with_subnet=False))
        if verbose:
            if status:
                print('SUCCESS: ', end='')
            else:
                print('FAILURE: ', end='')
            print('ping from {} to {} '.format(self.name,
                                               destination_address.get_addr(with_subnet=False)))
        return status


class Node(Namespace):
    """
    This class represents the end devices on a network. It inherits
    the Namespace class
    """

    def __init__(self, node_name):

        error_handling.type_verify('node_name', node_name, 'string', str)

        Namespace.__init__(self, node_name)

    def enable_ip_forwarding(self):
        """
        Enable IP forwarding in Node.
        This gives flexibility to user to use a 
        Node as a Router.
        """

        engine.en_ip_forwarding(self.id)


class Router(Namespace):
    """
    This class represents the intermediate routers in a networks. It inherits 
    the Namespace class
    """

    def __init__(self, router_name):

        error_handling.type_verify('router_name', router_name, 'string', str)

        Namespace.__init__(self, router_name)

        # Enable forwarding
        engine.en_ip_forwarding(self.id)
