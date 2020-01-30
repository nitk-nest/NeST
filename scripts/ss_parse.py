# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import re
import subprocess
import json
import time
import utils
import numpy as np

INTERVAL = 0.2
RUN_TIME = 60
STATS_TO_PLOT = list()


def run_ss(cmd):
	"""
	runs the ss command

	:param cmd: conmplete ss command to be run
	:type cmd: string

	:return output of the ss command
	"""
	proc = subprocess.Popen(cmd.split(), stdin=subprocess.PIPE,
	                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	(stdout, stderr) = proc.communicate()

	# if there is an error
	if stderr:
		return None

	return stdout.decode();  # stdout is a bytes-like object. Hence the usage of decode()


def parse(ns_name, param_list, destination_ip):
	"""
	parses the required data from ss command's output

	:param param_list: list of the stats to be parsed
	:type param_list: list of string
	:param destination_ip: destination ip address of the socket
	:type destination_ip: string

	return
	"""
	command = 'ip netns exec {} ss -i dst {}'.format(ns_name, destination_ip)
	json_stats = {}
	cur_time = 0.0


	# list to store the stats obtained at every interval
	stats_list = list()

	# This loop runs the ss command every `INTERVAL`s for `RUN_TIME`s
	while cur_time <= RUN_TIME:
		stats = run_ss(command)


		# a dictionary where stats are stored with param name as key
		stats_dict = {}
		for param in param_list:
			pattern = r'\s' + re.escape(param) + r'[\s:]\w+\.?\w*(?:[\/\,]\w+\.?\w*)*\s'

			# result list stores all the string that is matched by the `pattern`
			result_list = re.findall(pattern, stats)

			# pattern to match the required param in result_list
			pattern = r'^' + re.escape(param) + r'[:\s]'
			val = ''
			for result in result_list:
				result = result.strip()
				if re.search(pattern, result):
					val = re.sub(pattern, '', result)

			# rtt has both avg and dev rtt separated by a /
			
			try:
				if param == 'rtt':
					avg_rtt = val.split('/')[0]
					dev_rtt = val.split('/')[1]
					stats_dict['rtt'] = avg_rtt
					stats_dict['dev_rtt'] = dev_rtt
				else:
					stats_dict[param] = val
			except:
				pass

		# a dictionary to store the stats_dict with timestamp as key
		time_dict = {}
		time_dict[cur_time] = stats_dict
		stats_list.append(time_dict)
		time.sleep(INTERVAL)
		cur_time = cur_time + INTERVAL

	# convert the stats list to a json array
	json_stats = json.dumps(stats_list, indent=4)

	output_to_file(json_stats)


def output_to_file(json_stats):
	"""
	outputs statistics to a json file

	:param json_stats: parsed ss statistics
	:type json_stats: json
	"""

	timestamp = time.strftime("%d-%m-%Y-%H:%M:%S")
	filename = str(timestamp) + ' ss-parse-results.json'
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
		for key, val in stat.items():
			x.append(float(key))
			for param, value in val.items():
				if param in parameters:
					try:
						print(param_map[param], index)
						y[param_map[param], index] = float(value)
					except:
						y[param_map[param], index] = 0.0
			index = index + 1
	# utils.plot(x, y, xlabel='time', ylabel=parameter)
	utils.sub_plots(x, y, xlabel='time', ylabel=parameters)
	f.close()

# TODO: Integrate with nest


def parse_ss(ns_name, destination_ip, stats_to_plot, run_time):
	param_list = ['cwnd', 'rwnd', 'rtt', 'ssthresh', 'rto', 'lastack']
	global RUN_TIME
	RUN_TIME = run_time
	global STATS_TO_PLOT 
	STATS_TO_PLOT = stats_to_plot
	parse(ns_name, param_list, destination_ip)



