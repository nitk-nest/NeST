# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import subprocess

def run_test_commands(cmd):
    proc = subprocess.Popen(cmd.split())


def run_netserver(ns_name):
    cmd = 'ip netns exec {} netserver'.format(ns_name)
    run_test_commands(cmd)


def run_netperf(ns_name, destination_ip):
	cmd = 'ip netns exec {} netperf -H {}'.format(ns_name, destination_ip)
	run_test_commands(cmd)
