# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# Keep track of all information required to provide 
# services by module. It's essentially a fancy global
# variable :P

# Information kept track are of
# 1. User
# 2. Topology
# 3. Tests to be run

class User():
    """
    User info like user_id and group_id stored here.
    """

    user_id = ''
    group_id = ''

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
class Configuration():

    # config contains the info about topology created
    # and the tests to be run
    config = {
        'namespaces': [],
        'tests': []
    }

    # Pointer to config['namespaces']
    # Used for efficiency
    namespaces_pointer = {}

    def __init__():
        pass

    @staticmethod
    def add_namespace(id, ns_name):
        """
        Add namespace to config

        :param id: namepspace id
        :type id: string
        :param ns_name: namespace name
        :type ns_name: string
        """

        namespaces = Configuration.get_namespaces()

        namespaces.append({
            'id': id,
            'name': ns_name,
            'interfaces': []
        })

        Configuration.namespaces_pointer[id] = {
            'pos': len(namespaces)-1,
            'interfaces_pointer': {}
        }
    
    @staticmethod
    def add_interface(ns_id, id, int_name):
        """
        Add interface to config

        :param ns_id: namepspace id
        :type ns_id: string
        :param id: interface id
        :type id: string
        :param int_name: interface name
        :type id: string
        """

        # TODO: classes not added yet to list
        interfaces = Configuration.get_interfaces(ns_id)

        interfaces.append({
            'id': id,
            'name': int_name,
            'qdiscs': []
        }) 

        Configuration.namespaces_pointer[ns_id]['interfaces_pointer'][id] = {
            'pos': len(interfaces)-1
        }

    @staticmethod
    def add_qdisc(ns_id, int_id, kind, handle, parent = ''):
        """
        Add qdisc to config

        :param ns_id: namepspace id
        :type ns_id: string
        :param int_id: interface id
        :type int_id: string
        :param kind: qdisc kind
        :type kind: string
        :param handle: qdisc handle
        :type handle: string
        :param parent: qdisc parent
        :type parent: string
        """

        qdiscs = Configuration.get_qdiscs(ns_id, int_id)
        qdiscs.append({
            'kind': kind,
            'handle': handle,
            'parent': parent
        })

    @staticmethod
    def delete_qdisc(ns_id, int_id, handle):
        """
        Delete qdisc from config

        :param ns_id: namepspace id
        :type ns_id: string
        :param int_id: interface id
        :type int_id: string
        :param handle: qdisc handle
        :type handle: string
        """

        qdiscs = Configuration.get_qdiscs(ns_id, int_id)
        counter = 0
        for qdisc in qdiscs:
            if qdisc['handle'] == handle:
                qdiscs.pop(counter)
                break
            counter += 1

    @staticmethod
    def add_test(name, src_ns, dst_ns, dst_addr, start_t, stop_t, n_flows):
        """
        Add test to config

        :param name: test name
        :type name: string
        :param src_ns: source namespace
        :type src_ns: string
        :param dst_ns: destination namespace
        :type dst_ns: string
        :param start_t: Start time
        :type start_t: int
        :param stop_t: Stop time
        :type stop_t: int
        :param n_flows: number of flows
        :type n_flows: int
        """
        
        tests = Configuration.get_tests()
        tests.append({
            'name': name,
            'src_ns': src_ns,
            'dst_ns': dst_ns,
            'dst_addr': dst_addr,
            'start_t': start_t,
            'stop_t': stop_t,
            'n_flows': n_flows
        })


    @staticmethod
    def get_config():
        return Configuration.config

    @staticmethod
    def get_tests():
        return Configuration.config['tests']

    @staticmethod
    def get_namespaces():
        return Configuration.config['namespaces']

    @staticmethod
    def get_namespace(ns_id, with_interfaces_pointer = False):
        """
        Get namespace given it's id

        :param ns_id: namespace id
        :type ns_id: string
        :param with_interfaces_pointer: If should return interfaces_pointer for the namespace
        :type with_interfaces_pointer: bool
        """

        namespaces = Configuration.get_namespaces()
        namespace_pointer = Configuration.namespaces_pointer[ns_id]
        namespace = namespaces[namespace_pointer['pos']]

        if with_interfaces_pointer:
            return (namespace_pointer['interfaces_pointer'], namespace)
        else:
            return namespace

    @staticmethod
    def get_interfaces(ns_id):
        """
        Get all interfaces in the namespace

        :param ns_id: namespace id
        :type ns_id: string
        """

        namespace = Configuration.get_namespace(ns_id)
        interfaces = namespace['interfaces']
        
        return interfaces

    @staticmethod
    def get_interface(ns_id, int_id):
        """
        Get interface in namespace `ns_id` with interface
        `int_id`

        :param ns_id: namespace id
        :type ns_id: string
        :param int_id: interface id
        :type int_id: string
        """

        (interfaces_pointer, namespace) = Configuration.get_namespace(ns_id, with_interfaces_pointer=True)
        interfaces = Configuration.get_interfaces(ns_id)
        interface_pointer = interfaces_pointer[int_id]
        interface = interfaces[interface_pointer['pos']]

        return interface

    @staticmethod
    def get_qdiscs(ns_id, int_id):
        """
        Get qdiscs in namespace `ns_id` with interface
        `int_id`

        :param ns_id: namespace id
        :type ns_id: string
        :param int_id: interface id
        :type int_id: string
        """

        interface = Configuration.get_interface(ns_id, int_id)
        qdiscs = interface['qdiscs']

        return qdiscs

    def dump():
        """
        Dump generated config. (for debugging purposes)
        """

        import json

        print('Config')
        print('------')
        print(json.dumps(Configuration.config, indent = 4))

        # print()
        # print('Pointers')
        # print('--------')
        # print(json.dumps(Configuration.namespaces_pointer, indent = 4))
