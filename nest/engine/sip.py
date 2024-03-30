# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2024 NITK Surathkal

"""SIP commands"""

import subprocess
import signal
from .exec import exec_subprocess, exec_exp_commands


def run_sip_server(ns_name, port, scenario="basic", xml_file=None):
    """
    Run SIP server on provided namespace

    Parameters
    ----------
    ns_name : str
        Name of the server namespace
    port: int
        Port number to run the server on.
    scenario : str
        Specifies the scenario to be run for the experiment.
        (uses "basic" as default)
    xml_file : Path
        Specifies the path to an XML scenario file for the SIPp test.
        (Used only when scenario is "xml")
    Returns
    -------
    int
        return code of the command executed
    """
    if scenario == "branch":
        scenario_option = "-sn branchs"
    elif scenario == "xml":
        scenario_option = f"-sf {xml_file}"
    else:
        scenario_option = "-sn uas"

    cmd_string = f"""ip netns exec {ns_name} sipp -p {port}\
    {scenario_option} -bg"""

    return exec_subprocess(cmd_string)


# pylint: disable=too-many-arguments
def run_sip_client(
    ns_name,
    destination_ip,
    port,
    duration,
    out,
    err,
    scenario="basic",
    xml_file=None,
    callrate=None,
):
    """
    Run SIP client

    Parameters
    ----------
    ns_name : str
        Name of the client namespace
    destination_ip : str
        IP address of the server namespace
    port : int
        port number of the server at which the SIP application is running
    duration : int
        Specifies the duration of the SIPp test.
    out : Path
        Path to the file where standard output will be redirected.
    err : Path
        Path to the file where standard error will be redirected.
    scenario : string
        Specifies the scenario to be run for the experiment
        (uses "basic" as default)
    xml_file : Path
        Specifies the path to an XML scenario file for the SIPp test.
        (Used only when scenario is "xml")
    Returns
    -------
    int
        return code of the command executed
    """

    if scenario == "branch":
        scenario_option = "-sn branchc"
    elif scenario == "xml":
        scenario_option = f"-sf {xml_file}"
    else:
        scenario_option = "-sn uac"

    callrate_option = ""
    if callrate is not None:
        callrate_option = "-r " + str(callrate)

    cmd_string = f"""ip netns exec {ns_name} \
    sipp {scenario_option} {destination_ip}:{port} -trace_stat \
    -stf {out.name} {callrate_option}
    """

    return exec_exp_commands(
        cmd_string,
        stdout=subprocess.PIPE,
        stderr=err,
        timeout=duration,
        signal_on_timeout=signal.SIGTERM,
    )
