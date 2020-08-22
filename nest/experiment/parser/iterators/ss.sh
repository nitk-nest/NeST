# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

# Runs the ss command

INTERVAL=0.2

destination_ip="$1"
duration="$2"
filter="$3"
start_time="$4"

command="ss -i -t "$filter" -n dst $destination_ip"

sleep $start_time

# Runs the ss command for `duration`s every `INTERVAL`s
# Output of each ss iteration is separated by `---`
for i in $(seq 1 $INTERVAL $duration); do
	echo "timestamp:$(date +%s.%N)"
	eval $command
	if [ $? -ne 0 ]; then
		exit 1
	fi
	echo "---"
	sleep $INTERVAL
done
