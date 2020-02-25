# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import re
import json
import subprocess
import time
import numpy as np
from . import utils

INTERVAL = 0.2
RUN_TIME = 60
STATS_TO_PLOT = list()


def run_tc(cmd):
    """
    runs the tc command

    :param cmd: conmplete tc command to be run
    :type cmd: string

    :return output of the tc command
    """
    proc = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = proc.communicate()

    # if there is an error
    if stderr:
        return None

    return stdout.decode()  # stdout is a bytes-like object. Hence the usage of decode()


def parse(ns_name, stats_to_plot):
    """

    parses the required data from tc-qdisc output

    :param ns_name: namespace name of the router
    :type ns_name: string
    """

    command = 'ip netns exec {} tc -s -j qdisc show'.format(ns_name)
    json_stats = {}
    cur_time = 0.0


    # list to store the stats obtained at every interval
    stats_list = list()

    # This loop runs the ss command every `INTERVAL`s for `RUN_TIME`s
    while cur_time <= RUN_TIME:
        stats = run_tc(command)

        # pattern to remove the options key as some of it's child keys
        # were not in the required format
        pattern = r'"options": {(.|\n)*?},'
        stats = re.sub(pattern, '', stats)

        stats = json.loads(stats)

        # a dictionary to store the stats_dict with timestamp as key
        time_dict = {}
        time_dict[cur_time] = stats
        stats_list.append(time_dict)
        time.sleep(INTERVAL)
        cur_time = cur_time + INTERVAL

        json_stats = json.dumps(stats_list, indent=4)

    output_to_file(json_stats)


def output_to_file(json_stats):
    """
    outputs statistics to a json file

    :param json_stats: parsed tc statistics
    :type json_stats: json
    """

    timestamp = time.strftime("%d-%m-%Y-%H:%M:%S")
    filename = str(timestamp) + ' tc-parse-results.json'
    with open(filename, 'w') as f:
        f.write(json_stats)

    if len(STATS_TO_PLOT) > 0:
        parse_and_plot(filename, STATS_TO_PLOT)

def parse_and_plot(filename, parameters):
    """

    parses the json from a file and plots time vs `parameter`

    :param filename: path of the json file
    :type filename: string
    :param paramter: parameters to be plotted (eg. cwnd, rtt)
    :type parameter: list of strings
    """

    f = open(filename, 'r')


    # stats stores the json object as list of dicts with timestamp as keys
    stats = json.load(f)


    x = list()
    y = np.empty((len(parameters), int(RUN_TIME/INTERVAL)+1))

    param_map = {}

    for i in range(len(parameters)):
        param_map[parameters[i]] = i

    # Loops through the list of dicts and stores the values of timestamps
    # in x and value of the required `paramter` in y for plotting
    index = 0
    for stat in stats:
        for timestamp, qdiscs in stat.items():
            x.append(float(timestamp))
            for qdisc in qdiscs:
                for param, value in qdisc.items():
                    if param in parameters:
                        try:
                            y[param_map[param], index] = float(value)
                        except:
                            y[param_map[param], index] = 0.0
            index = index + 1
    # utils.plot(x, y, xlabel='time', ylabel=parameter)
    utils.sub_plots(x, y, xlabel='time', ylabel=parameters)
    f.close()


def parse_qdisc(ns_name, stats_to_plot, run_time):
    param_list = ['bytes', 'drops', 'packets', 'qlen']
    global RUN_TIME
    RUN_TIME = run_time
    global STATS_TO_PLOT
    STATS_TO_PLOT = stats_to_plot
    parse(ns_name, stats_to_plot)


# parse_qdisc('71dedc7da6-2', ['bytes'], 2)
