# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

#!/bin/bash
# Runs the ss command

INTERVAL=0.2

destination_ip="$1"
duration="$2"
filter="$3"

command="ss -i  "$filter" -n dst $destination_ip"

# Runs the ss command for `duration`s every `INTERVAL`s
# Output of each ss iteration is separated by `---` 
for i in $(seq 1 $INTERVAL $duration); do
	echo "timestamp:$(date +%s.%N)"
	eval $command
	echo "---"
	sleep $INTERVAL
done
