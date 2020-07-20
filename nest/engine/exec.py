# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""Execute linux commands"""

import subprocess
import shlex

# Contain the entire log of commands run with stdout
# and stderr
LOGS = []
LOG_LEVEL = 0

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

        if LOG_LEVEL > 0:
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
