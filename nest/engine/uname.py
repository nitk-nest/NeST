# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""uname commands"""

from .exec import exec_subprocess


def get_kernel_version():
    """Get Linux kernel version of the system"""
    version = exec_subprocess("uname -r", output=True)
    return version.split("-", maxsplit=1)[0]
