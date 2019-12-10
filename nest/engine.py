# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019 NITK Surathkal

##########################################
# Note: This script should be run as root
##########################################

import os
import subprocess

def exec_subprocess(cmd, block = True):
	temp = subprocess.Popen(cmd.split())
	if block:
		temp.communicate()
	else:
		pass

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
    Create namespace with name `ns_name`
    if it doesn't already exist
    Delt namespace with name `ns_name`
    if it doesn't already exist
    """
    exec_subprocess('ip netns add ' + ns_name)

def delete_ns(ns_name):
    """
    Drops the namespace with name `ns_name`
    if it already exists.
    """
    exec_subprocess('ip netns del ' + ns_name)

def en_ip_forwarding(ns_name):
    """
    Enables ip forwarding in the namespace 
    `ns_name`. Used for routers
    """
    exec_subprocess('ip netns exec ' + ns_name + ' sysctl -w net.ipv4.ip_forward=1')

#TODO: delete a veth
def create_veth(dev_name1, dev_name2):
    """
    Create a veth interfaces with endpoints
    `dev_name1` and `dev_name2`
    """
    exec_subprocess('ip link add ' + dev_name1 +' type veth peer name ' + dev_name2)

def add_int_to_ns(ns_name, dev_name):
    """
    Add interface `dev_name` to namespace `ns_name`
    """
    exec_subprocess('ip link set ' + dev_name + ' netns ' + ns_name)

def set_int_up(ns_name, dev_name):
    """
    Set interface `dev_name` in namespace `ns_name` to up
    """
    exec_subprocess('ip netns exec ' + ns_name + ' ip link set dev ' + dev_name + ' up')

# Use this function for `high level convinience`
def setup_veth(ns_name1, ns_name2, dev_name1, dev_name2):
    """
    Sets up veth connection with interafaces `dev_name1` and
    `dev_name2` associated with namespaces `ns_name1` and 
    `ns_name2` respectively. The interfaces are set up as well.
    """
    create_veth(dev_name1, dev_name2)
    add_int_to_ns(ns_name1, dev_name1)
    add_int_to_ns(ns_name2, dev_name2)
    set_int_up(ns_name1, dev_name1)
    set_int_up(ns_name2, dev_name2)

def create_peer(peer_name):
    """
    Creates a peer with the name `peer_name` and adds it to 
    the existing topology.
    """
    create_ns(peer_name)

def create_router(router_name):
    """
    Creates a router with the name `router_name` and adds it to 
    the existing topology.
    """
    create_ns(router_name)
    en_ip_forwarding(router_name)

def connect(peer_name=None, router_name1=None, router_name2=None):
    """
    Connects two namespaces(a peer with a router or two routers) and
    returns the created interface names
    """
    if(peer_name):
        peer_int = peer_name + '-' + router_name1
        router_int = router_name1 + '-' + peer_name
        setup_veth(peer_name, router_name1, peer_int, router_int)
        return (peer_int, router_int)
    else:
        router1_int = router_name1 + '-' + router_name2
        router2_int = router_name2 + '-' + router_name1
        setup_veth(router_name1, router_name2, router1_int, router2_int)
        return (router1_int, router2_int)

def assign_ip(host_name, dev_name, ip_address):
    """
    Assigns ip address `ip_address` to interface
    `dev_name` in host `host_name`.
    """
    #TODO: Support for ipv6
    exec_subprocess('ip netns exec ' + host_name + ' ip address add ' + ip_address + ' dev ' + dev_name)

def add_route(host_name, dest_ip, next_hop_ip, via_int):
    """
    Adds a route in routing table of `host_name`.
    `dest_ip` is the destination ip for the route.
    `next_hop_ip` is the IP of the very next device 
    (next hop) in the route.
    `via_int` is the corresponding interface in the
    host.
    """
    exec_subprocess('ip netns exec {} ip route add {} via {} dev {}'.format(host_name, dest_ip, next_hop_ip, via_int))

def set_interface_mode(ns_name, dev_name, mode):
    exec_subprocess('ip netns exec ' + ns_name + ' ip link set dev ' + dev_name + ' ' + mode)

# Only bandwith and latency is considered
# Assuming tc on egress 
# Using Netem
def add_traffic_control(host_name, dev_name, rate, latency):
    """
    Add traffic control to `host_name`.
    `rate` of the bandwidth
    `latency` of the link
    """
    exec_subprocess('ip netns exec {} tc qdisc add dev {} root netem rate {} latency {}'.format(host_name, dev_name, rate, latency))
