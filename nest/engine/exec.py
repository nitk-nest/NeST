# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Execute Linux commands"""

import logging
import shlex
import subprocess
from subprocess import Popen, PIPE


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

    with Popen(temp_cmd, stdout=PIPE, stderr=PIPE, shell=shell) as proc:

        (stdout, _) = proc.communicate()
        logger.trace(cmd)

        if output:
            return stdout.decode()
        return proc.returncode


def exec_subprocess_with_live_output(cmd):
    """
    Executes command and prints live output to stdout.

    For eg., if ping command is used, then the output for each
    packet is printed live to stdout.

    Parameters
    ----------
    cmd : str
        Command to be executed

    Returns
    -------
    int
        Return code recieved after executing the command
    """
    # Inspired from:
    # https://fabianlee.org/2019/09/15/python-getting-live-output-from-subprocess-using-poll/

    with Popen(cmd.split(), stdout=PIPE) as process:
        while True:
            output = process.stdout.readline()
            if process.poll() is not None:
                break
            if output:
                print(output.decode(), end="")

        # Print an extra newline at the end
        print()
        logger.trace(cmd)
        return process.poll()


def exec_exp_commands(cmd, stdout=PIPE, stderr=PIPE, timeout=None):
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
    with Popen(shlex.split(cmd), stdout=stdout, stderr=stderr) as proc:
        logger.trace(cmd)
        try:
            proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            stderr.write(b"Connection timeout")
        return proc.returncode
