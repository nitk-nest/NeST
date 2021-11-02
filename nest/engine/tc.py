# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Traffic control management"""

from .exec import exec_subprocess

# Only bandwidth and latency is considered
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
    exec_subprocess(
        f"tc -n {host_name} qdisc add dev {dev_name} root"
        f" netem rate {rate} latency {latency}"
    )


def add_qdisc(ns_name, dev_name, qdisc, parent="", handle="", **kwargs):
    """
    Add a qdisc on an device

    Parameters
    ----------
    ns_name : str
        name of the namespace
    qdisc : str
        qdisc used on the device
    parent : str
        id of the parent class in major:minor form(optional) (Default value = '')
    handle : str
        id of the qdisc in major:0 form (Default value = '')
    dev_name : str
        name of the device
    """
    if parent and parent != "root":
        parent = "parent " + parent

    if handle:
        handle = "handle " + handle

    qdisc_params = ""
    for param, value in kwargs.items():
        qdisc_params += param + " " + value + " "

    exec_subprocess(
        f"tc -n {ns_name} qdisc add dev {dev_name}"
        f" {parent} {handle} {qdisc} {qdisc_params}"
    )


def change_qdisc(ns_name, dev_name, qdisc, parent, handle, **kwargs):
    """
    Change a qdisc that is already present on an device

    Parameters
    ----------
    ns_name : str
        name of the namespace
    qdisc : str
        qdisc used on the device
    parent : str
        id of the parent class in major:minor form(optional)
    handle : str
        id of the qdisc in major:0 form
    dev_name : str
        name of the device
    """
    if parent and parent != "root":
        parent = "parent " + parent

    if handle:
        handle = "handle " + handle

    qdisc_params = ""
    for param, value in kwargs.items():
        qdisc_params += param + " " + value + " "

    exec_subprocess(
        f"tc -n {ns_name} qdisc change dev {dev_name}"
        f" {parent} {handle} {qdisc} {qdisc_params}"
    )


def replace_qdisc(ns_name, dev_name, qdisc, parent="", handle="", **kwargs):
    """
    Replace a qdisc that is already present on an device

    Parameters
    ----------
    ns_name : str
        name of the namespace
    qdisc : str
        qdisc used on the device
    parent : str
        id of the parent class in major:minor form(optional) (Default value = '')
    handle : str
        id of the qdisc in major:0 form (Default value = '')
    dev_name : str
        name of the device
    """
    if parent and parent != "root":
        parent = "parent " + parent

    if handle:
        handle = "handle " + handle

    qdisc_params = ""
    for param, value in kwargs.items():
        qdisc_params += param + " " + value + " "

    exec_subprocess(
        f"tc -n {ns_name} qdisc replace dev {dev_name}"
        f" {parent} {handle} {qdisc} {qdisc_params}"
    )


def delete_qdisc(ns_name, dev_name, parent, handle):
    """
    Delete a qdisc on an device

    Parameters
    ----------
    ns_name : str
        name of the namespace
    qdisc : str
        qdisc used on the device
    parent : str
        id of the parent class in major:minor form(optional) (Default value = '')
    handle : str
        id of the qdisc in major:0 form (Default value = '')
    dev_name : str
        name of the device
    """
    if parent and parent != "root":
        parent = "parent " + parent

    if handle:
        handle = "handle " + handle

    exec_subprocess(f"tc -n {ns_name} qdisc del dev {dev_name} {parent} {handle}")


def add_class(ns_name, dev_name, parent, qdisc, classid="", **kwargs):
    """
    Add a class to a qdisc

    Parameters
    ----------
    ns_name : str
        name of the namespace
    parent : str
        id of the parent class in major:minor form(optional)
    qdisc : str
        qdisc used on the device
    classid : str
        id of the class in major:minor form (Default value = '')
    dev_name : str
        name of the device
    """
    if classid:
        classid = "classid " + classid

    qdisc_params = ""
    for param, value in kwargs.items():
        qdisc_params += param + " " + value + " "

    exec_subprocess(
        f"tc -n {ns_name} class add dev {dev_name} parent {parent}"
        f" {classid} {qdisc} {qdisc_params}"
    )


def change_class(ns_name, dev_name, parent, qdisc, classid, **kwargs):
    """
    Change a class that is already present on an device

    Parameters
    ----------
    ns_name : str
        name of the namespace
    parent : str
        id of the parent class in major:minor form(optional)
    qdisc : str
        qdisc used on the device
    classid : str
        id of the class in major:minor form (Default value = '')
    dev_name : str
        name of the device
    """

    if classid:
        classid = "classid " + classid

    qdisc_params = ""
    for param, value in kwargs.items():
        qdisc_params += param + " " + value + " "

    exec_subprocess(
        f"tc -n {ns_name} class change dev {dev_name} parent {parent}"
        f" {classid} {qdisc} {qdisc_params}"
    )


def delete_class(ns_name, dev_name, parent, classid):
    """
    Delete a class added to a qdisc
    Parameters
    ----------
    ns_name : str
        name of the namespace
    dev_name : str
        name of the device
    parent : str
        id of the parent class in major:minor form(optional)
    classid : str
        id of the class in major:minor form (Default value = '')
    """

    if classid:
        classid = "classid " + classid

    exec_subprocess(
        f"tc -n {ns_name} class delete dev {dev_name} parent {parent}" f" {classid}"
    )


# pylint: disable=too-many-arguments
def add_filter(
    ns_name, dev_name, protocol, priority, filtertype, parent="", handle="", **kwargs
):
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
        qdisc used on the device
    dev_name : str
        name of the device
    """

    # TODO: Check if protocol can be removed from the arguments since it's always IP

    if parent and parent != "root":
        parent = "parent " + parent

    if handle:
        handle = "handle " + handle

    filter_params = ""

    for param, value in kwargs.items():
        filter_params += param + " " + value + " "

    exec_subprocess(
        f"tc -n {ns_name} filter add dev {dev_name} {parent} {handle}"
        f" protocol {protocol} prio {priority} {filtertype} {filter_params}"
    )


def delete_filter(ns_name, dev_name, parent, handle):
    """
    Delete filter on a class

    Parameters
    ----------
    ns_name : str
        name of the namespace
    dev_name : str
        name of the device
    parent : str
        id of the parent class in major:minor form(optional) (Default value = '')
    handle : str
        id of the filter (Default value = '')
    """
    if parent and parent != "root":
        parent = "parent " + parent

    if handle:
        handle = "handle " + handle

    exec_subprocess(f"tc -n {ns_name} filter delete dev {dev_name} {parent} {handle}")


def get_tc_version():
    """
    check for current tc version

    Returns
    -------
    str
        string containing current tc version
    """
    return exec_subprocess("tc -V", output=True)
