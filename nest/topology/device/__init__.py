# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2022 NITK Surathkal

"""
This folder contains classes for various network devices
in Linux, for eg., Veth, Ifb
"""

from .device import Device
from .ifb import Ifb
from .veth_end import VethEnd
