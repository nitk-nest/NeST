# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

import re
import subprocess
import json
import time
import numpy as np

from . import utils
import nest.topology.id_generator as id_generator
from .results import SsResults

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
	command = 'ip netns exec {} ss -i {} dst {}'.format(ns_name, 'dport != 12865 and sport != 12865' , destination_ip) #NOTE: Assumed that netserver runs on default port
	json_stats = {}
	cur_time = 0.0


	# list to store the stats obtained at every interval
	stats_list = list()

	# This loop runs the ss command every `INTERVAL`s for `RUN_TIME`s
	while cur_time <= RUN_TIME:
		stats = run_ss(command)


		# a dictionary where stats are stored with param name as key
		stats_dict_list = []
		for param in param_list:
			pattern = r'\s' + re.escape(param) + r'[\s:]\w+\.?\w*(?:[\/\,]\w+\.?\w*)*\s'

			# result list stores all the string that is matched by the `pattern`
			result_list = re.findall(pattern, stats)

			#fill the empty list with empty dicts
			if len(stats_dict_list) == 0:
				stats_dict_list = [{} for i in range(len(result_list))]


			# pattern to match the required param in result_list
			pattern = r'^' + re.escape(param) + r'[:\s]'
			val = ''
			for i in range(len(result_list)):
				result = result_list[i].strip()
				if re.search(pattern, result):
					val = re.sub(pattern, '', result)
					# remove the units at the end
					val = re.sub(r'[A-Za-z]', '', val)
				try:
					# rtt has both avg and dev rtt separated by a /
					if param == 'rtt':
						avg_rtt = val.split('/')[0]
						dev_rtt = val.split('/')[1]
						stats_dict_list[i]['rtt'] = avg_rtt
						stats_dict_list[i]['dev_rtt'] = dev_rtt
					else:
						stats_dict_list[i][param] = val
				except:
					pass

		# a dictionary to store the stats_dict_list with timestamp as key
		time_dict = {}
		time_dict[cur_time] = stats_dict_list
		stats_list.append(time_dict)
		time.sleep(INTERVAL)
		cur_time = cur_time + INTERVAL

	SsResults.add_result(ns_name, stats_list)


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
						y[param_map[param], index] = float(value)
					except:
						y[param_map[param], index] = 0.0
			index = index + 1
	# utils.plot(x, y, xlabel='time', ylabel=parameter)
	utils.sub_plots(x, y, xlabel='time', ylabel=parameters)
	f.close()

# TODO: Integrate with nest


def parse_ss(ns_name, destination_ip, stats_to_plot, start_time, run_time):
	param_list = ['cwnd', 'rwnd', 'rtt', 'ssthresh', 'rto', 'delivery_rate']
	global RUN_TIME
	RUN_TIME = run_time
	global STATS_TO_PLOT 
	STATS_TO_PLOT = stats_to_plot
	
	if(start_time != 0):
		time.sleep(start_time)

	parse(ns_name, param_list, destination_ip)



