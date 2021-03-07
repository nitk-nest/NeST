# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

"""
NeST keeps track of all global variables here

WARNING: Avoid adding new variables in this file
         until its the only last resort
"""

# Keeps track if DAD checked or not,
# whenever new topology is defined
IS_DAD_CHECKED = False

# Keeps track if address is IPv6 or not for DAD check
IS_IPV6 = False
