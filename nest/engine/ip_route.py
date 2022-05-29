# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""IP route commands"""

import os
import json
import inspect
from pathlib import Path
from datetime import datetime
from .exec import exec_subprocess


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
    exec_subprocess(
        f"ip netns exec {host_name} ip route add {dest_ip}"
        f" via {next_hop_ip} dev {via_int}"
    )


def get_route(host_name, *args):
    """
    Get the routes from the routing table of a Node.

    Parameters
    ----------
    host_name : str
        name of the host namespace
    args : Interface
        Interface object of which route information want
    """
    data = exec_subprocess(f"ip netns exec {host_name} ip -j route", False, True)
    date = datetime.now().strftime("%d-%m-%y_%I:%M:%S_%p")
    data = json.loads(data)
    path = Path(inspect.stack()[2][1]).parent
    file_name = Path(inspect.stack()[2][1]).stem
    json_string = json.dumps(data, indent=4)
    complete_name = os.path.join(path, file_name + "_" + date)

    # pylint: disable=bare-except,consider-using-f-string
    if not args:
        try:
            os.mkdir(f"{file_name}_{date}")
        except:
            pass
        with open(
            os.path.join(f"{complete_name}", "All_route_of_" + f"{host_name}.json"), "a"
        ) as outfile:
            outfile.write("{}\n".format(json_string))

    for temp in args:
        try:
            temp.get_address()
        except:
            print(
                " Argument "
                + f" {temp}"
                + "is not in required form, Argument should be Interface"
            )
            continue
        try:
            os.mkdir(f"{complete_name}")
        except:
            pass
        if temp.node_id is not f"{host_name}":
            print(
                "Interface "
                + f"{temp.name}"
                + " is not belong to host "
                + f"{host_name}"
            )
            continue

        for i in data:
            if "prefsrc" in i.keys() and i[
                "prefsrc"
            ].strip() == temp.get_address().get_addr(False):
                with open(
                    os.path.join(
                        f"{complete_name}",
                        "route_info_of_interface_" + f"{temp.name}.json",
                    ),
                    "a",
                ) as outfile:
                    outfile.write("{}\n".format(json.dumps(i, indent=4)))
