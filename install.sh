# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2019-2020 NITK Surathkal

#!/bin/bash

# Checks if the user is a root user or not
if [ ${USER} != "root" ]
then
    echo "${0}: Permission denied. Try running the program as root user" 1>&2 
    
    exit 1
fi

curr_path="$(pwd)"

# "Install" nest
ln -s "$curr_path/run-nest.py" /usr/bin/nest

# Add nest manpage to system
mkdir -p /usr/local/man/man1
cp man/nest.1 /usr/local/man/man1/nest.1
gzip /usr/local/man/man1/nest.1

# Add bash-completion
cp bash-completion/nest-completion.sh /usr/share/bash-completion/completions/
echo "source /usr/share/bash-completion/completions/nest-completion.sh" >> ~/.bashrc

# Equivalent to compiling the ~/.bashrc file
source ~/.bashrc
