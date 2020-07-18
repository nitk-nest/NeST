# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""
Engine sub-package provides low-level APIs to other sub-packages

All the calls to linux kernel happens in this module.
"""

import os
import subprocess
import shlex

### LEGACY SUPPORT ###
# Engine previously was a single file.
# Now we are making it into a module. Since this
# shift can take some time, we will maintain the
# old version below, until the module is fully
# implemented.


# Contain the entire log of commands run with stdout
# and stderr
# NOTE: Will be useful to be imported as variable to
# arguments.py if user requests more logging
LOGS = []
log_level = 0

# NOTE: verbose or log_level?


def exec_subprocess(cmd, block=True, shell=False, verbose=False, output=False):
    """
    Executes a command

    Parameters
    ----------
    cmd : str
        command to be executed
    block : boolean
        A flag to indicate whether the command
        should be executed asynchronously (Default value = True)
    shell : boolean
        Spawns a shell and executes the command if true (Default value = False)
    verbose : boolean
        if commands run should be printed (Default value = False)
    output : boolean
        True if the output of the `cmd` is to be returned (Default value = False)

    Returns
    -------

    """

    # TODO: Commands with pipes are easily executed when
    # they are run within a shell.
    # But it may not be the most efficient way.

    # Logging
    if verbose:
        print('[INFO] ' + cmd)

    temp_cmd = cmd
    if shell is False:
        temp_cmd = cmd.split()

    proc = subprocess.Popen(temp_cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=shell)
    if block:
        (stdout, stderr) = proc.communicate()

        if log_level > 0:
            LOGS.append({
                'cmd': cmd,
                'stdout': stdout.decode(),
                'stderr': stderr.decode()
            })
        if output:
            return stdout.decode()

    else:
        pass

    return proc.returncode

def exec_exp_commands(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=None):
    """
    executes experiment related commands like ss, tc and netperf

    Parameters
    ----------
    cmd : str
        command to be executed
    stdout : File
        temp file(usually) to store the output (Default value = subprocess.PIPE)
    stderr : File
        temp file(usually) to store errors, if any (Default value = subprocess.PIPE)
    timeout :
         (Default value = None)

    Returns
    -------


    """
    proc = subprocess.Popen(shlex.split(cmd), stdout=stdout, stderr=stderr)
    try:
        proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        stderr.write(b'Connection timeout')
    return proc.returncode

############################################
# CONVENTION:
# - In parameter list, namespace
#   names come before interface names.
# - Peers are entities at the ends points of
#   the network.
# - Router connects atleast 2 hosts.
# - Host represents either peer or router
#   based on context.
############################################


def create_ns(ns_name):
    """
    Create namespace if it doesn't already exist

    Parameters
    ----------
    ns_name : str
        namespace name
    """
    exec_subprocess('ip netns add ' + ns_name)


def delete_ns(ns_name):
    """
    Drops the namespace if it already exists.

    Parameters
    ----------
    ns_name : str
        namespace name
    """
    exec_subprocess('ip netns del ' + ns_name)


def en_ip_forwarding(ns_name):
    """
    Enables ip forwarding in a namespace. Used for routers

    Parameters
    ----------
    ns_name : str
        namespace name
    """
    exec_subprocess('ip netns exec ' + ns_name +
                    ' sysctl -w net.ipv4.ip_forward=1')


def ping(ns_name, dest_addr):
    """
    Send a ping packet from ns_name to dest_addr
    if possible

    Parameters
    ----------
    ns_name : str
        namespace name
    dest_addr : str
        address to ping to

    Returns
    -------
    bool
        success of ping
    """
    status = exec_subprocess(
        'ip netns exec {} ping -c1 -q {}'.format(ns_name, dest_addr))
    return status == 0

#TODO: delete a veth


def create_veth(dev_name1, dev_name2):
    """
    Create a veth pair with endpoint interfaces `dev_name1`
    and `dev_name2`

    Parameters
    ----------
    dev_name1 : str
    dev_name2 : str
    """
    exec_subprocess('ip link add ' + dev_name1 +
                    ' type veth peer name ' + dev_name2)


def create_ifb(dev_name):
    """
    Create a IFB

    Parameters
    ----------
    dev_name : str
        interface names
    """

    exec_subprocess('ip link add {} type ifb'.format(dev_name))


def add_int_to_ns(ns_name, dev_name):
    """
    Add interface to a namespace

    Parameters
    ----------
    ns_name : str
        namespace name
    dev_name : str
        interface name
    """
    exec_subprocess('ip link set ' + dev_name + ' netns ' + ns_name)


def set_int_up(ns_name, dev_name):
    """
    Set interface mode to up

    Parameters
    ----------
    ns_name : str
        namespace name
    dev_name : str
        interface name
    """
    exec_subprocess('ip netns exec ' + ns_name +
                    ' ip link set dev ' + dev_name + ' up')


def setup_veth(ns_name1, ns_name2, dev_name1, dev_name2):
    """
    Sets up veth connection between interafaces. The interfaces are
    set up as well.

    The connections are made between `dev_name1` in `ns_name1` and
    `dev_name2` in `ns_name2`

    Parameters
    ----------
    ns_name1 : str
    dev_name1 : str
    dev_name2 : str
    ns_name2 : str
    """
    create_veth(dev_name1, dev_name2)
    add_int_to_ns(ns_name1, dev_name1)
    add_int_to_ns(ns_name2, dev_name2)
    set_int_up(ns_name1, dev_name1)
    set_int_up(ns_name2, dev_name2)


def setup_ifb(ns_name, dev_name):
    """
    Sets up an IFB device. The device is setup as well.

    Parameters
    ----------
    ns_name : str
        namespace name
    dev_name : str
        name of IFB
    """

    create_ifb(dev_name)
    add_int_to_ns(ns_name, dev_name)
    set_int_up(ns_name, dev_name)


def create_peer(peer_name):
    """
    Creates a peer and adds it to the existing topology.

    Parameters
    ----------
    peer_name : str
        name of the peer namespace
    """
    create_ns(peer_name)


def create_router(router_name):
    """
    Creates a router and adds it to
    the existing topology.

    Parameters
    ----------
    router_name : str
        name of the router namespace
    """
    create_ns(router_name)
    en_ip_forwarding(router_name)


def assign_ip(host_name, dev_name, ip_address):
    """
    Assigns ip address to interface

    Parameters
    ----------
    host_name : str
        name of the host namespace
    dev_name : str
        name of the interface
    ip_address : str
        ip address to be assigned to the interface
    """
    #TODO: Support for ipv6
    exec_subprocess('ip netns exec ' + host_name +
                    ' ip address add ' + ip_address + ' dev ' + dev_name)


def add_route(host_name, dest_ip, next_hop_ip, via_int):
    """
    Adds a route in routing table of host.

    Parameters
    ----------
    host_name : str
        name of the host namespace
    dest_ip : str
        the destination ip for the route
    next_hop_ip : str
        IP of the very next interface
    via_int : str
        the corresponding interface in the host
    """
    exec_subprocess('ip netns exec {} ip route add {} via {} dev {}'.format(
        host_name, dest_ip, next_hop_ip, via_int))


def set_interface_mode(ns_name, dev_name, mode):
    """

    Parameters
    ----------
    ns_name : str
    dev_name : str
    mode : str
    """
    exec_subprocess('ip netns exec ' + ns_name +
                    ' ip link set dev ' + dev_name + ' ' + mode)


def kill_all_processes(ns_name):
    """
    Kill all processes in a namespace

    Parameters
    ----------
    ns_name : str
        Namespace name
    """

    exec_subprocess('kill $(ip netns pids {ns_name})'.format(
        ns_name=ns_name), shell=True)

# Only bandwith and latency is considered
# Assuming tc on egress
# Using Netem


def add_traffic_control(host_name, dev_name, rate, latency):
    """
    Add traffic control to host

    Parameters
    ----------
    host_name : str
        name of the host namespace
    rate : str
        rate of the bandwidth
    latency : str
        latency of the link
    dev_name : str
    """
    exec_subprocess('ip netns exec {} tc qdisc add dev {} root netem rate {} latency {}'.format(
        host_name, dev_name, rate, latency))


def run_iperf_server(ns_name):
    """
    Run Iperf Server on a namesapce

    Parameters
    ----------
    ns_name : str
        name of the server namespace
    """
    #TODO: iperf3?
    exec_subprocess('ip netns {} iperf -s'.format(ns_name))


def run_iperf_client(ns_name, server_ip):
    """
    Run Iperf Client

    Parameters
    ----------
    ns_name : str
        name of the client namespace
    server_ip : str
        the ip of server to which it has to connect
    """
    exec_subprocess('ip netns {} iperf -c {}'.format(ns_name, server_ip))


def add_qdisc(ns_name, dev_name, qdisc, parent='', handle='', **kwargs):
    """
    Add a qdisc on an interface

    Parameters
    ----------
    ns_name : str
        name of the namespace
    qdisc : str
        qdisc used on the interface
    parent : str
        id of the parent class in major:minor form(optional) (Default value = '')
    handle : str
        id of the qdisc in major:0 form (Default value = '')
    dev_name : str
        name of the interface
    """
    if parent and parent != 'root':
        parent = 'parent ' + parent

    if handle:
        handle = 'handle ' + handle

    qdisc_params = ''
    for param, value in kwargs.items():
        qdisc_params += param + ' ' + value + ' '

    exec_subprocess('ip netns exec {} tc qdisc add dev {} {} {} {} {}'.format(
        ns_name, dev_name, parent, handle, qdisc, qdisc_params))


def change_qdisc(ns_name, dev_name, qdisc, parent='', handle='', **kwargs):
    """
    Change a qdisc that is already present on an interface

    Parameters
    ----------
    ns_name : str
        name of the namespace
    qdisc : str
        qdisc used on the interface
    parent : str
        id of the parent class in major:minor form(optional) (Default value = '')
    handle : str
        id of the qdisc in major:0 form (Default value = '')
    dev_name : str
        name of the interface
    """
    if parent and parent != 'root':
        parent = 'parent ' + parent

    if handle:
        handle = 'handle ' + handle

    qdisc_params = ''
    for param, value in kwargs.items():
        qdisc_params += param + ' ' + value + ' '

    exec_subprocess('ip netns exec {} tc qdisc change dev {} {} {} {} {}'.format(
        ns_name, dev_name, parent, handle, qdisc, qdisc_params))


def replace_qdisc(ns_name, dev_name, qdisc, parent='', handle='', **kwargs):
    """
    Replace a qdisc that is already present on an interface

    Parameters
    ----------
    ns_name : str
        name of the namespace
    qdisc : str
        qdisc used on the interface
    parent : str
        id of the parent class in major:minor form(optional) (Default value = '')
    handle : str
        id of the qdisc in major:0 form (Default value = '')
    dev_name : str
        name of the interface
    """
    if parent and parent != 'root':
        parent = 'parent ' + parent

    if handle:
        handle = 'handle ' + handle

    qdisc_params = ''
    for param, value in kwargs.items():
        qdisc_params += param + ' ' + value + ' '

    exec_subprocess('ip netns exec {} tc qdisc replace dev {} {} {} {} {}'.format(
        ns_name, dev_name, parent, handle, qdisc, qdisc_params))


def delete_qdisc(ns_name, dev_name, parent='', handle=''):
    """
    Add a qdisc on an interface

    Parameters
    ----------
    ns_name : str
        name of the namespace
    qdisc : str
        qdisc used on the interface
    parent : str
        id of the parent class in major:minor form(optional) (Default value = '')
    handle : str
        id of the qdisc in major:0 form (Default value = '')
    dev_name : str
        name of the interface
    """
    if parent and parent != 'root':
        parent = 'parent ' + parent

    if handle:
        handle = 'handle ' + handle

    exec_subprocess('ip netns exec {} tc qdisc del dev {} {} {}'.format(
        ns_name, dev_name, parent, handle))


def add_class(ns_name, dev_name, parent, qdisc, classid='', **kwargs):
    """
    Add a class to a qdisc

    Parameters
    ----------
    ns_name : str
        name of the namespace
    parent : str
        id of the parent class in major:minor form(optional)
    qdisc : str
        qdisc used on the interface
    classid : str
        id of the class in major:minor form (Default value = '')
    dev_name : str
        name of the interface
    """
    if classid:
        classid = 'classid ' + classid

    qdisc_params = ''
    for param, value in kwargs.items():
        qdisc_params += param + ' ' + value + ' '

    exec_subprocess('ip netns exec {} tc class add dev {} parent {} {} {} {}'.format(
        ns_name, dev_name, parent, classid, qdisc, qdisc_params))


def change_class(ns_name, dev_name, parent, qdisc, classid='', **kwargs):
    """
    Change a class that is already present on an interface

    Parameters
    ----------
    ns_name : str
        name of the namespace
    parent : str
        id of the parent class in major:minor form(optional)
    qdisc : str
        qdisc used on the interface
    classid : str
        id of the class in major:minor form (Default value = '')
    dev_name : str
        name of the interface
    """

    if classid:
        classid = 'classid ' + classid

    qdisc_params = ''
    for param, value in kwargs.items():
        qdisc_params += param + ' ' + value + ' '

    exec_subprocess('ip netns exec {} tc class change dev {} parent {} {} {} {}'.format(
        ns_name, dev_name, parent, classid, qdisc, qdisc_params))

def add_filter(ns_name, dev_name, protocol, priority, filtertype, parent='', handle='', **kwargs):
    """
    Add a filter to a class

    Parameters
    ----------
    ns_name : str
        name of the namespace
    protocol : str
        protocol used
    priority : str
        priority
    filtertype : str
        one of the available filters
    parent : str
        id of the parent class in major:minor form(optional) (Default value = '')
    handle : str
        id of the filter (Default value = '')
    qdisc : str
        qdisc used on the interface
    dev_name : str
        name of the interface
    """

    # TODO: Check if protocol can be removed from the arguments since it's always ip

    if parent and parent != 'root':
        parent = 'parent ' + parent

    if handle:
        handle = 'handle ' + handle

    filter_params = ''

    for param, value in kwargs.items():
        filter_params += param + ' ' + value + ' '

    exec_subprocess('ip netns exec {} tc filter add dev {} {} {} protocol {} prio {} {} {}'
                    .format(ns_name, dev_name, parent, handle, protocol, priority, filtertype,
                            filter_params))


def configure_kernel_param(ns_name, prefix, param, value):
    """
    Configure kernel parameters using sysctl

    Parameters
    ----------
    ns_name : str
        name of the namespace
    prefix : str
        path for the sysctl command
    param : str
        kernel parameter to be configured
    value : str
        value of the parameter
    """
    exec_subprocess(
        'ip netns exec {} sysctl -q -w {}{}={}'.format(ns_name, prefix, param, value))


def read_kernel_param(ns_name, prefix, param):
    """
    Read kernel parameters using sysctl

    Parameters
    ----------
    ns_name : str
        name of the namespace
    prefix : str
        path for the sysctl command
    param : str
        kernel parameter to be read

    Returns
    -------
    str
        value of the `param`
    """
    value = exec_subprocess(
        f'ip netns exec {ns_name} sysctl -n {prefix}{param}', output=True)
    return value.rstrip('\n')


def get_kernel_version():
    """Get linux kernel version of the system"""
    version = exec_subprocess('uname -r', output=True)
    return version.split('-')[0]


# def del_class(ns_name, dev_name, parent, qdisc, classid = ''):
#     """
#     Add a class to a qdisc

#     :param ns_name: name of the namespace
#     :type ns_name: str
#     :dev_name: name of the interface
#     :type dev_name: str
#     :param parent: id of the parent class in major:minor form(optional)
#     :type parent: str
#     :param qdisc: qdisc used on the interface
#     :type qdisc: str
#     :param classid: id of the class in major:minor form
#     :type classid: str
#     """

#     if classid:
#         classid = 'classid ' + classid

#     exec_subprocess('ip netns exec {} tc class add dev {} parent {} {} {}'.format(
#           ns_name, dev_name, parent, classid, qdisc))

# def del_filter(ns_name, dev_name, protocol, priority, filtertype, flowid, parent = '',
# handle = ''):
#     """
#     Add a filter to a class

#     :param ns_name: name of the namespace
#     :type ns_name: str
#     :dev_name: name of the interface
#     :type dev_name: str
#     :param protocol: protocol used
#     :type protocol: str
#     :param priority: priority
#     :type priority: str
#     :param filtertype: one of the available filters
#     :type filtertype: str
#     :param flowid: classid of the class where the traffic is enqueued
#       if the traffic passes the filter
#     :type flowid: str
#     :param parent: id of the parent class in major:minor form(optional)
#     :type parent: str
#     :param handle: id of the filter
#     :type handle: str
#     :param qdisc: qdisc used on the interface
#     :type qdisc: str
#     """

#     if parent and parent != 'root':
#         parent = 'parent ' + parent

#     if handle:
#         handle = 'handle ' + handle

#     filter_params = ''

#     for param, value in kwargs.items():
#         filter_params = param +' ' + value +' '

#     exec_subprocess(
#           'ip netns exec {} tc filter add dev {} {} {} protocol {} priority {} {} {} flowid {}'
#           .format(ns_name, dev_name, parent, handle, protocol, priority, filtertype,
#           filter_params, flowid))
