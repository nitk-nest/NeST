# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Execute Linux commands"""

import logging
import shlex
import subprocess


logger = logging.getLogger(__name__)

# pylint: disable=inconsistent-return-statements
def exec_subprocess(cmd, shell=False, output=False):
    """
    Executes a command

    Parameters
    ----------
    cmd : str
        command to be executed
    shell : boolean
        Spawns a shell and executes the command if true
        (Default value = False)
    output : boolean
        True if the output of the `cmd` is to be returned
        (Default value = False)

    Returns
    -------
    int
        Return code received after executing the command
    """

    # TODO: Commands with pipes are easily executed when
    # they are run within a shell.
    # But it may not be the most efficient way.

    temp_cmd = cmd
    if shell is False:
        temp_cmd = cmd.split()
    proc = subprocess.Popen(
        temp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell
    )

    (stdout, _) = proc.communicate()
    logger.trace(cmd)

    if output:
        return stdout.decode()
    return proc.returncode


def exec_exp_commands(
    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=None
):
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
    int
        Return code recieved after executing the command
    """
    proc = subprocess.Popen(shlex.split(cmd), stdout=stdout, stderr=stderr)
    logger.trace(cmd)
    try:
        proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        stderr.write(b"Connection timeout")
    return proc.returncode
